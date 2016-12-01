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
    PartialDownloadError, _WebToNormalContextFactory, FileBodyProducer,
    CookieAgent, GzipDecoder, ContentDecoderAgent, RedirectAgent,
)


class _URL(tuple):
    """
    A parsed URL.

    At some point this should be replaced with a better URL implementation.
    """
    def __new__(self, scheme, host, port, path):
        return tuple.__new__(_URL, (scheme, host, port, path))


    def __init__(self, scheme, host, port, path):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.path = path


def _parse(url, defaultPort=None):
    """
    Split the given URL into the scheme, host, port, and path.

    @type url: C{bytes}
    @param url: An URL to parse.

    @type defaultPort: C{int} or C{None}
    @param defaultPort: An alternate value to use as the port if the URL does
    not include one.

    @return: A four-tuple of the scheme, host, port, and path of the URL.  All
    of these are C{bytes} instances except for port, which is an C{int}.
    """
    url = url.strip()
    parsed = http.urlparse(url)
    scheme = parsed[0]
    path = urlunparse((b'', b'') + parsed[2:])

    if defaultPort is None:
        if scheme == b'https':
            defaultPort = 443
        else:
            defaultPort = 80

    host, port = parsed[1], defaultPort
    if b':' in host:
        host, port = host.split(b':')
        try:
            port = int(port)
        except ValueError:
            port = defaultPort

    if path == b'':
        path = b'/'

    return _URL(scheme, host, port, path)


def _makeGetterFactory(url, factoryFactory, contextFactory=None,
                       *args, **kwargs):
    """
    Create and connect an HTTP page getting factory.

    Any additional positional or keyword arguments are used when calling
    C{factoryFactory}.

    @param factoryFactory: Factory factory that is called with C{url}, C{args}
        and C{kwargs} to produce the getter

    @param contextFactory: Context factory to use when creating a secure
        connection, defaulting to C{None}

    @return: The factory created by C{factoryFactory}
    """
    scheme, host, port, path = _parse(url)
    factory = factoryFactory(url, *args, **kwargs)
    if scheme == b'https':
        from twisted.internet import ssl
        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    return factory


# The code which follows is based on the new HTTP client implementation.  It
# should be significantly better than anything above, though it is not yet
# feature equivalent.

from twisted.web.error import SchemeNotSupported
from twisted.web._newclient import Response
from ._newclient import Request, HTTP11ClientProtocol
from twisted.web._newclient import ResponseDone, ResponseFailed
from twisted.web._newclient import RequestNotSent, RequestTransmissionFailed
from twisted.web._newclient import (
    ResponseNeverReceived, PotentialDataLoss, _WrapperException)

try:
    from twisted.internet.ssl import ClientContextFactory
except ImportError:
    class WebClientContextFactory(object):
        """
        A web context factory which doesn't work because the necessary SSL
        support is missing.
        """
        def getContext(self, hostname, port):
            raise NotImplementedError("SSL support unavailable")
else:
    class WebClientContextFactory(ClientContextFactory):
        """
        A web context factory which ignores the hostname and port and does no
        certificate verification.
        """
        def getContext(self, hostname, port):
            return ClientContextFactory.getContext(self)



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



class _AgentBase(object):
    """
    Base class offering common facilities for L{Agent}-type classes.

    @ivar _reactor: The C{IReactorTime} implementation which will be used by
        the pool, and perhaps by subclasses as well.

    @ivar _pool: The L{HTTPConnectionPool} used to manage HTTP connections.
    """

    def __init__(self, reactor, pool):
        if pool is None:
            pool = HTTPConnectionPool(reactor, False)
        self._reactor = reactor
        self._pool = pool


    def _computeHostValue(self, scheme, host, port):
        """
        Compute the string to use for the value of the I{Host} header, based on
        the given scheme, host name, and port number.
        """
        if (scheme, port) in (('http', 80), ('https', 443)):
            return host
        return '%s:%d' % (host, port)


    def _requestWithEndpoint(self, key, endpoint, method, parsedURI,
                             headers, bodyProducer, requestPath):
        """
        Issue a new request, given the endpoint and the path sent as part of
        the request.
        """
        # Create minimal headers, if necessary:
        if headers is None:
            headers = Headers()
        if not headers.hasHeader('host'):
            #headers = headers.copy()  # not supported in twisted <= 11.1, and it doesn't affects us
            headers.addRawHeader(
                'host', self._computeHostValue(parsedURI.scheme, parsedURI.host,
                                               parsedURI.port))

        d = self._pool.getConnection(key, endpoint)
        def cbConnected(proto):
            return proto.request(
                Request(method, requestPath, headers, bodyProducer,
                        persistent=self._pool.persistent))
        d.addCallback(cbConnected)
        return d



class Agent(_AgentBase):
    """
    L{Agent} is a very basic HTTP client.  It supports I{HTTP} and I{HTTPS}
    scheme URIs (but performs no certificate checking by default).

    @param pool: A L{HTTPConnectionPool} instance, or C{None}, in which case a
        non-persistent L{HTTPConnectionPool} instance will be created.

    @ivar _contextFactory: A web context factory which will be used to create
        SSL context objects for any SSL connections the agent needs to make.

    @ivar _connectTimeout: If not C{None}, the timeout passed to C{connectTCP}
        or C{connectSSL} for specifying the connection timeout.

    @ivar _bindAddress: If not C{None}, the address passed to C{connectTCP} or
        C{connectSSL} for specifying the local address to bind to.

    @since: 9.0
    """

    def __init__(self, reactor, contextFactory=WebClientContextFactory(),
                 connectTimeout=None, bindAddress=None,
                 pool=None):
        _AgentBase.__init__(self, reactor, pool)
        self._contextFactory = contextFactory
        self._connectTimeout = connectTimeout
        self._bindAddress = bindAddress


    def _wrapContextFactory(self, host, port):
        """
        Create and return a normal context factory wrapped around
        C{self._contextFactory} in such a way that C{self._contextFactory} will
        have the host and port information passed to it.

        @param host: A C{str} giving the hostname which will be connected to in
            order to issue a request.

        @param port: An C{int} giving the port number the connection will be
            on.

        @return: A context factory suitable to be passed to
            C{reactor.connectSSL}.
        """
        return _WebToNormalContextFactory(self._contextFactory, host, port)


    def _getEndpoint(self, scheme, host, port):
        """
        Get an endpoint for the given host and port, using a transport
        selected based on scheme.

        @param scheme: A string like C{'http'} or C{'https'} (the only two
            supported values) to use to determine how to establish the
            connection.

        @param host: A C{str} giving the hostname which will be connected to in
            order to issue a request.

        @param port: An C{int} giving the port number the connection will be
            on.

        @return: An endpoint which can be used to connect to given address.
        """
        kwargs = {}
        if self._connectTimeout is not None:
            kwargs['timeout'] = self._connectTimeout
        kwargs['bindAddress'] = self._bindAddress
        if scheme == 'http':
            return TCP4ClientEndpoint(self._reactor, host, port, **kwargs)
        elif scheme == 'https':
            return SSL4ClientEndpoint(self._reactor, host, port,
                                      self._wrapContextFactory(host, port),
                                      **kwargs)
        else:
            raise SchemeNotSupported("Unsupported scheme: %r" % (scheme,))


    def request(self, method, uri, headers=None, bodyProducer=None):
        """
        Issue a new request.

        @param method: The request method to send.
        @type method: C{str}

        @param uri: The request URI send.
        @type uri: C{str}

        @param headers: The request headers to send.  If no I{Host} header is
            included, one will be added based on the request URI.
        @type headers: L{Headers}

        @param bodyProducer: An object which will produce the request body or,
            if the request body is to be empty, L{None}.
        @type bodyProducer: L{IBodyProducer} provider

        @return: A L{Deferred} which fires with the result of the request (a
            L{twisted.web.iweb.IResponse} provider), or fails if there is a
            problem setting up a connection over which to issue the request.
            It may also fail with L{SchemeNotSupported} if the scheme of the
            given URI is not supported.
        @rtype: L{Deferred}
        """
        parsedURI = _parse(uri)
        try:
            endpoint = self._getEndpoint(parsedURI.scheme, parsedURI.host,
                                         parsedURI.port)
        except SchemeNotSupported:
            return defer.fail(Failure())
        key = (parsedURI.scheme, parsedURI.host, parsedURI.port)
        return self._requestWithEndpoint(key, endpoint, method, parsedURI,
                                         headers, bodyProducer, parsedURI.path)



class ProxyAgent(_AgentBase):
    """
    An HTTP agent able to cross HTTP proxies.

    @ivar _proxyEndpoint: The endpoint used to connect to the proxy.

    @since: 11.1
    """

    def __init__(self, endpoint, reactor=None, pool=None):
        if reactor is None:
            from twisted.internet import reactor
        _AgentBase.__init__(self, reactor, pool)
        self._proxyEndpoint = endpoint


    def request(self, method, uri, headers=None, bodyProducer=None):
        """
        Issue a new request via the configured proxy.
        """
        # Cache *all* connections under the same key, since we are only
        # connecting to a single destination, the proxy:
        key = ("http-proxy", self._proxyEndpoint)

        # To support proxying HTTPS via CONNECT, we will use key
        # ("http-proxy-CONNECT", scheme, host, port), and an endpoint that
        # wraps _proxyEndpoint with an additional callback to do the CONNECT.
        return self._requestWithEndpoint(key, self._proxyEndpoint, method,
                                         _parse(uri), headers, bodyProducer,
                                         uri)



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
