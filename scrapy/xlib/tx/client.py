# -*- test-case-name: twisted.web.test.test_webclient,twisted.web.test.test_agent -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
HTTP client.
"""

from __future__ import division, absolute_import

import os

try:
    from urlparse import urlunparse
    from urllib import splithost, splittype
except ImportError:
    from urllib.parse import splithost, splittype
    from urllib.parse import urlunparse as _urlunparse

    def urlunparse(parts):
        result = _urlunparse(tuple([p.decode("charmap") for p in parts]))
        return result.encode("charmap")
import zlib

from zope.interface import implementer

from twisted.python import log
from twisted.python.failure import Failure
from twisted.web import http
from twisted.internet import defer, protocol, task, reactor
from twisted.internet.interfaces import IProtocol
from twisted.internet.endpoints import TCP4ClientEndpoint, SSL4ClientEndpoint
from twisted.python import failure
from twisted.python.components import proxyForInterface
from twisted.web import error
from twisted.web.iweb import UNKNOWN_LENGTH, IBodyProducer, IResponse
from twisted.web.http_headers import Headers

from twisted.web.client import (
    PartialDownloadError, FileBodyProducer,
    CookieAgent, GzipDecoder, ContentDecoderAgent, RedirectAgent,
    Agent, ProxyAgent,
)

# The code which follows is based on the new HTTP client implementation.  It
# should be significantly better than anything above, though it is not yet
# feature equivalent.

from twisted.web._newclient import Response
from ._newclient import HTTP11ClientProtocol
from twisted.web._newclient import ResponseDone, ResponseFailed
from twisted.web._newclient import RequestNotSent, RequestTransmissionFailed
from twisted.web._newclient import (
    ResponseNeverReceived, PotentialDataLoss, _WrapperException)


class _HTTP11ClientFactory(protocol.Factory):
    """
    A factory for L{HTTP11ClientProtocol}, used by L{HTTPConnectionPool}.

    @ivar _quiescentCallback: The quiescent callback to be passed to protocol
        instances, used to return them to the connection pool.

    @since: 11.1
    """
    def __init__(self, quiescentCallback):
        self._quiescentCallback = quiescentCallback


    def buildProtocol(self, addr):
        return HTTP11ClientProtocol(self._quiescentCallback)



class _RetryingHTTP11ClientProtocol(object):
    """
    A wrapper for L{HTTP11ClientProtocol} that automatically retries requests.

    @ivar _clientProtocol: The underlying L{HTTP11ClientProtocol}.

    @ivar _newConnection: A callable that creates a new connection for a
        retry.
    """

    def __init__(self, clientProtocol, newConnection):
        self._clientProtocol = clientProtocol
        self._newConnection = newConnection


    def _shouldRetry(self, method, exception, bodyProducer):
        """
        Indicate whether request should be retried.

        Only returns C{True} if method is idempotent, no response was
        received, the reason for the failed request was not due to
        user-requested cancellation, and no body was sent. The latter
        requirement may be relaxed in the future, and PUT added to approved
        method list.
        """
        if method not in ("GET", "HEAD", "OPTIONS", "DELETE", "TRACE"):
            return False
        if not isinstance(exception, (RequestNotSent, RequestTransmissionFailed,
                                      ResponseNeverReceived)):
            return False
        if isinstance(exception, _WrapperException):
            for failure in exception.reasons:
                if failure.check(defer.CancelledError):
                    return False
        if bodyProducer is not None:
            return False
        return True


    def request(self, request):
        """
        Do a request, and retry once (with a new connection) it it fails in
        a retryable manner.

        @param request: A L{Request} instance that will be requested using the
            wrapped protocol.
        """
        d = self._clientProtocol.request(request)

        def failed(reason):
            if self._shouldRetry(request.method, reason.value,
                                 request.bodyProducer):
                return self._newConnection().addCallback(
                    lambda connection: connection.request(request))
            else:
                return reason
        d.addErrback(failed)
        return d



class HTTPConnectionPool(object):
    """
    A pool of persistent HTTP connections.

    Features:
     - Cached connections will eventually time out.
     - Limits on maximum number of persistent connections.

    Connections are stored using keys, which should be chosen such that any
    connections stored under a given key can be used interchangeably.

    Failed requests done using previously cached connections will be retried
    once if they use an idempotent method (e.g. GET), in case the HTTP server
    timed them out.

    @ivar persistent: Boolean indicating whether connections should be
        persistent. Connections are persistent by default.

    @ivar maxPersistentPerHost: The maximum number of cached persistent
        connections for a C{host:port} destination.
    @type maxPersistentPerHost: C{int}

    @ivar cachedConnectionTimeout: Number of seconds a cached persistent
        connection will stay open before disconnecting.

    @ivar retryAutomatically: C{boolean} indicating whether idempotent
        requests should be retried once if no response was received.

    @ivar _factory: The factory used to connect to the proxy.

    @ivar _connections: Map (scheme, host, port) to lists of
        L{HTTP11ClientProtocol} instances.

    @ivar _timeouts: Map L{HTTP11ClientProtocol} instances to a
        C{IDelayedCall} instance of their timeout.

    @since: 12.1
    """

    _factory = _HTTP11ClientFactory
    maxPersistentPerHost = 2
    cachedConnectionTimeout = 240
    retryAutomatically = True

    def __init__(self, reactor, persistent=True):
        self._reactor = reactor
        self.persistent = persistent
        self._connections = {}
        self._timeouts = {}


    def getConnection(self, key, endpoint):
        """
        Supply a connection, newly created or retrieved from the pool, to be
        used for one HTTP request.

        The connection will remain out of the pool (not available to be
        returned from future calls to this method) until one HTTP request has
        been completed over it.

        Afterwards, if the connection is still open, it will automatically be
        added to the pool.

        @param key: A unique key identifying connections that can be used
            interchangeably.

        @param endpoint: An endpoint that can be used to open a new connection
            if no cached connection is available.

        @return: A C{Deferred} that will fire with a L{HTTP11ClientProtocol}
           (or a wrapper) that can be used to send a single HTTP request.
        """
        # Try to get cached version:
        connections = self._connections.get(key)
        while connections:
            connection = connections.pop(0)
            # Cancel timeout:
            self._timeouts[connection].cancel()
            del self._timeouts[connection]
            if connection.state == "QUIESCENT":
                if self.retryAutomatically:
                    newConnection = lambda: self._newConnection(key, endpoint)
                    connection = _RetryingHTTP11ClientProtocol(
                        connection, newConnection)
                return defer.succeed(connection)

        return self._newConnection(key, endpoint)


    def _newConnection(self, key, endpoint):
        """
        Create a new connection.

        This implements the new connection code path for L{getConnection}.
        """
        def quiescentCallback(protocol):
            self._putConnection(key, protocol)
        factory = self._factory(quiescentCallback)
        return endpoint.connect(factory)


    def _removeConnection(self, key, connection):
        """
        Remove a connection from the cache and disconnect it.
        """
        connection.transport.loseConnection()
        self._connections[key].remove(connection)
        del self._timeouts[connection]


    def _putConnection(self, key, connection):
        """
        Return a persistent connection to the pool. This will be called by
        L{HTTP11ClientProtocol} when the connection becomes quiescent.
        """
        if connection.state != "QUIESCENT":
            # Log with traceback for debugging purposes:
            try:
                raise RuntimeError(
                    "BUG: Non-quiescent protocol added to connection pool.")
            except:
                log.err()
            return
        connections = self._connections.setdefault(key, [])
        if len(connections) == self.maxPersistentPerHost:
            dropped = connections.pop(0)
            dropped.transport.loseConnection()
            self._timeouts[dropped].cancel()
            del self._timeouts[dropped]
        connections.append(connection)
        cid = self._reactor.callLater(self.cachedConnectionTimeout,
                                      self._removeConnection,
                                      key, connection)
        self._timeouts[connection] = cid


    def closeCachedConnections(self):
        """
        Close all persistent connections and remove them from the pool.

        @return: L{defer.Deferred} that fires when all connections have been
            closed.
        """
        results = []
        for protocols in self._connections.itervalues():
            for p in protocols:
                results.append(p.abort())
        self._connections = {}
        for dc in self._timeouts.values():
            dc.cancel()
        self._timeouts = {}
        return defer.gatherResults(results).addCallback(lambda ign: None)



class _ReadBodyProtocol(protocol.Protocol):
    """
    Protocol that collects data sent to it.

    This is a helper for L{IResponse.deliverBody}, which collects the body and
    fires a deferred with it.

    @ivar deferred: See L{__init__}.
    @ivar status: See L{__init__}.
    @ivar message: See L{__init__}.

    @ivar dataBuffer: list of byte-strings received
    @type dataBuffer: L{list} of L{bytes}
    """

    def __init__(self, status, message, deferred):
        """
        @param status: Status of L{IResponse}
        @ivar status: L{int}

        @param message: Message of L{IResponse}
        @type message: L{bytes}

        @param deferred: deferred to fire when response is complete
        @type deferred: L{Deferred} firing with L{bytes}
        """
        self.deferred = deferred
        self.status = status
        self.message = message
        self.dataBuffer = []


    def dataReceived(self, data):
        """
        Accumulate some more bytes from the response.
        """
        self.dataBuffer.append(data)


    def connectionLost(self, reason):
        """
        Deliver the accumulated response bytes to the waiting L{Deferred}, if
        the response body has been completely received without error.
        """
        if reason.check(ResponseDone):
            self.deferred.callback(b''.join(self.dataBuffer))
        elif reason.check(PotentialDataLoss):
            self.deferred.errback(
                PartialDownloadError(self.status, self.message,
                                     b''.join(self.dataBuffer)))
        else:
            self.deferred.errback(reason)



def readBody(response):
    """
    Get the body of an L{IResponse} and return it as a byte string.

    This is a helper function for clients that don't want to incrementally
    receive the body of an HTTP response.

    @param response: The HTTP response for which the body will be read.
    @type response: L{IResponse} provider

    @return: A L{Deferred} which will fire with the body of the response.
    """
    d = defer.Deferred()
    response.deliverBody(_ReadBodyProtocol(response.code, response.phrase, d))
    return d



__all__ = [
    'PartialDownloadError',
    'ResponseDone', 'Response', 'ResponseFailed', 'Agent', 'CookieAgent',
    'ProxyAgent', 'ContentDecoderAgent', 'GzipDecoder', 'RedirectAgent',
    'HTTPConnectionPool', 'readBody']
