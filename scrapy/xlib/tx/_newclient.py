# -*- test-case-name: twisted.web.test.test_newclient -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
An U{HTTP 1.1<http://www.w3.org/Protocols/rfc2616/rfc2616.html>} client.

The way to use the functionality provided by this module is to:

  - Connect a L{HTTP11ClientProtocol} to an HTTP server
  - Create a L{Request} with the appropriate data
  - Pass the request to L{HTTP11ClientProtocol.request}
  - The returned Deferred will fire with a L{Response} object
  - Create a L{IProtocol} provider which can handle the response body
  - Connect it to the response with L{Response.deliverBody}
  - When the protocol's C{connectionLost} method is called, the response is
    complete.  See L{Response.deliverBody} for details.

Various other classes in this module support this usage:

  - HTTPParser is the basic HTTP parser.  It can handle the parts of HTTP which
    are symmetric between requests and responses.

  - HTTPClientParser extends HTTPParser to handle response-specific parts of
    HTTP.  One instance is created for each request to parse the corresponding
    response.
"""

__metaclass__ = type

from zope.interface import implements

from twisted.python import log
from twisted.python.reflect import fullyQualifiedName
from twisted.python.failure import Failure
from twisted.internet.interfaces import IConsumer, IPushProducer
from twisted.internet.error import ConnectionDone
from twisted.internet.defer import Deferred, succeed, fail, maybeDeferred
from twisted.internet.defer import CancelledError
from twisted.internet.protocol import Protocol
from twisted.web.iweb import UNKNOWN_LENGTH, IResponse
from twisted.web.http import NO_CONTENT, NOT_MODIFIED
from twisted.web.http import _DataLoss, PotentialDataLoss
from twisted.web.http import _IdentityTransferDecoder, _ChunkedTransferDecoder

from twisted.web._newclient import (
    BadHeaders, ExcessWrite, ParseError, BadResponseVersion, _WrapperException,
    RequestGenerationFailed, RequestTransmissionFailed, ConnectionAborted,
    WrongBodyLength, ResponseDone, ResponseFailed, RequestNotSent, _callAppFunction,
    ResponseNeverReceived, HTTPParser, HTTPClientParser,
    LengthEnforcingConsumer, makeStatefulDispatcher, Response, ChunkedEncoder,
    TransportProxyProducer,
)

# States HTTPParser can be in
STATUS = 'STATUS'
HEADER = 'HEADER'
BODY = 'BODY'
DONE = 'DONE'


class Request:
    """
    A L{Request} instance describes an HTTP request to be sent to an HTTP
    server.

    @ivar method: The HTTP method to for this request, ex: 'GET', 'HEAD',
        'POST', etc.
    @type method: C{str}

    @ivar uri: The relative URI of the resource to request.  For example,
        C{'/foo/bar?baz=quux'}.
    @type uri: C{str}

    @ivar headers: Headers to be sent to the server.  It is important to
        note that this object does not create any implicit headers.  So it
        is up to the HTTP Client to add required headers such as 'Host'.
    @type headers: L{twisted.web.http_headers.Headers}

    @ivar bodyProducer: C{None} or an L{IBodyProducer} provider which
        produces the content body to send to the remote HTTP server.

    @ivar persistent: Set to C{True} when you use HTTP persistent connection.
    @type persistent: C{bool}
    """
    def __init__(self, method, uri, headers, bodyProducer, persistent=False):
        self.method = method
        self.uri = uri
        self.headers = headers
        self.bodyProducer = bodyProducer
        self.persistent = persistent


    def _writeHeaders(self, transport, TEorCL):
        hosts = self.headers.getRawHeaders('host', ())
        if len(hosts) != 1:
            raise BadHeaders("Exactly one Host header required")

        # In the future, having the protocol version be a parameter to this
        # method would probably be good.  It would be nice if this method
        # weren't limited to issuing HTTP/1.1 requests.
        requestLines = []
        requestLines.append(
            '%s %s HTTP/1.1\r\n' % (self.method, self.uri))
        if not self.persistent:
            requestLines.append('Connection: close\r\n')
        if TEorCL is not None:
            requestLines.append(TEorCL)
        for name, values in self.headers.getAllRawHeaders():
            requestLines.extend(['%s: %s\r\n' % (name, v) for v in values])
        requestLines.append('\r\n')
        transport.writeSequence(requestLines)


    def _writeToChunked(self, transport):
        """
        Write this request to the given transport using chunked
        transfer-encoding to frame the body.
        """
        self._writeHeaders(transport, 'Transfer-Encoding: chunked\r\n')
        encoder = ChunkedEncoder(transport)
        encoder.registerProducer(self.bodyProducer, True)
        d = self.bodyProducer.startProducing(encoder)

        def cbProduced(ignored):
            encoder.unregisterProducer()
        def ebProduced(err):
            encoder._allowNoMoreWrites()
            # Don't call the encoder's unregisterProducer because it will write
            # a zero-length chunk.  This would indicate to the server that the
            # request body is complete.  There was an error, though, so we
            # don't want to do that.
            transport.unregisterProducer()
            return err
        d.addCallbacks(cbProduced, ebProduced)
        return d


    def _writeToContentLength(self, transport):
        """
        Write this request to the given transport using content-length to frame
        the body.
        """
        self._writeHeaders(
            transport,
            'Content-Length: %d\r\n' % (self.bodyProducer.length,))

        # This Deferred is used to signal an error in the data written to the
        # encoder below.  It can only errback and it will only do so before too
        # many bytes have been written to the encoder and before the producer
        # Deferred fires.
        finishedConsuming = Deferred()

        # This makes sure the producer writes the correct number of bytes for
        # the request body.
        encoder = LengthEnforcingConsumer(
            self.bodyProducer, transport, finishedConsuming)

        transport.registerProducer(self.bodyProducer, True)

        finishedProducing = self.bodyProducer.startProducing(encoder)

        def combine(consuming, producing):
            # This Deferred is returned and will be fired when the first of
            # consuming or producing fires. If it's cancelled, forward that
            # cancellation to the producer.
            def cancelConsuming(ign):
                finishedProducing.cancel()
            ultimate = Deferred(cancelConsuming)

            # Keep track of what has happened so far.  This initially
            # contains None, then an integer uniquely identifying what
            # sequence of events happened.  See the callbacks and errbacks
            # defined below for the meaning of each value.
            state = [None]

            def ebConsuming(err):
                if state == [None]:
                    # The consuming Deferred failed first.  This means the
                    # overall writeTo Deferred is going to errback now.  The
                    # producing Deferred should not fire later (because the
                    # consumer should have called stopProducing on the
                    # producer), but if it does, a callback will be ignored
                    # and an errback will be logged.
                    state[0] = 1
                    ultimate.errback(err)
                else:
                    # The consuming Deferred errbacked after the producing
                    # Deferred fired.  This really shouldn't ever happen.
                    # If it does, I goofed.  Log the error anyway, just so
                    # there's a chance someone might notice and complain.
                    log.err(
                        err,
                        "Buggy state machine in %r/[%d]: "
                        "ebConsuming called" % (self, state[0]))

            def cbProducing(result):
                if state == [None]:
                    # The producing Deferred succeeded first.  Nothing will
                    # ever happen to the consuming Deferred.  Tell the
                    # encoder we're done so it can check what the producer
                    # wrote and make sure it was right.
                    state[0] = 2
                    try:
                        encoder._noMoreWritesExpected()
                    except:
                        # Fail the overall writeTo Deferred - something the
                        # producer did was wrong.
                        ultimate.errback()
                    else:
                        # Success - succeed the overall writeTo Deferred.
                        ultimate.callback(None)
                # Otherwise, the consuming Deferred already errbacked.  The
                # producing Deferred wasn't supposed to fire, but it did
                # anyway.  It's buggy, but there's not really anything to be
                # done about it.  Just ignore this result.

            def ebProducing(err):
                if state == [None]:
                    # The producing Deferred failed first.  This means the
                    # overall writeTo Deferred is going to errback now.
                    # Tell the encoder that we're done so it knows to reject
                    # further writes from the producer (which should not
                    # happen, but the producer may be buggy).
                    state[0] = 3
                    encoder._allowNoMoreWrites()
                    ultimate.errback(err)
                else:
                    # The producing Deferred failed after the consuming
                    # Deferred failed.  It shouldn't have, so it's buggy.
                    # Log the exception in case anyone who can fix the code
                    # is watching.
                    log.err(err, "Producer is buggy")

            consuming.addErrback(ebConsuming)
            producing.addCallbacks(cbProducing, ebProducing)

            return ultimate

        d = combine(finishedConsuming, finishedProducing)
        def f(passthrough):
            # Regardless of what happens with the overall Deferred, once it
            # fires, the producer registered way up above the definition of
            # combine should be unregistered.
            transport.unregisterProducer()
            return passthrough
        d.addBoth(f)
        return d


    def writeTo(self, transport):
        """
        Format this L{Request} as an HTTP/1.1 request and write it to the given
        transport.  If bodyProducer is not None, it will be associated with an
        L{IConsumer}.

        @return: A L{Deferred} which fires with C{None} when the request has
            been completely written to the transport or with a L{Failure} if
            there is any problem generating the request bytes.
        """
        if self.bodyProducer is not None:
            if self.bodyProducer.length is UNKNOWN_LENGTH:
                return self._writeToChunked(transport)
            else:
                return self._writeToContentLength(transport)
        else:
            self._writeHeaders(transport, None)
            return succeed(None)


    def stopWriting(self):
        """
        Stop writing this request to the transport.  This can only be called
        after C{writeTo} and before the L{Deferred} returned by C{writeTo}
        fires.  It should cancel any asynchronous task started by C{writeTo}.
        The L{Deferred} returned by C{writeTo} need not be fired if this method
        is called.
        """
        # If bodyProducer is None, then the Deferred returned by writeTo has
        # fired already and this method cannot be called.
        _callAppFunction(self.bodyProducer.stopProducing)



class HTTP11ClientProtocol(Protocol):
    """
    L{HTTP11ClientProtocol} is an implementation of the HTTP 1.1 client
    protocol.  It supports as few features as possible.

    @ivar _parser: After a request is issued, the L{HTTPClientParser} to
        which received data making up the response to that request is
        delivered.

    @ivar _finishedRequest: After a request is issued, the L{Deferred} which
        will fire when a L{Response} object corresponding to that request is
        available.  This allows L{HTTP11ClientProtocol} to fail the request
        if there is a connection or parsing problem.

    @ivar _currentRequest: After a request is issued, the L{Request}
        instance used to make that request.  This allows
        L{HTTP11ClientProtocol} to stop request generation if necessary (for
        example, if the connection is lost).

    @ivar _transportProxy: After a request is issued, the
        L{TransportProxyProducer} to which C{_parser} is connected.  This
        allows C{_parser} to pause and resume the transport in a way which
        L{HTTP11ClientProtocol} can exert some control over.

    @ivar _responseDeferred: After a request is issued, the L{Deferred} from
        C{_parser} which will fire with a L{Response} when one has been
        received.  This is eventually chained with C{_finishedRequest}, but
        only in certain cases to avoid double firing that Deferred.

    @ivar _state: Indicates what state this L{HTTP11ClientProtocol} instance
        is in with respect to transmission of a request and reception of a
        response.  This may be one of the following strings:

          - QUIESCENT: This is the state L{HTTP11ClientProtocol} instances
            start in.  Nothing is happening: no request is being sent and no
            response is being received or expected.

          - TRANSMITTING: When a request is made (via L{request}), the
            instance moves to this state.  L{Request.writeTo} has been used
            to start to send a request but it has not yet finished.

          - TRANSMITTING_AFTER_RECEIVING_RESPONSE: The server has returned a
            complete response but the request has not yet been fully sent
            yet.  The instance will remain in this state until the request
            is fully sent.

          - GENERATION_FAILED: There was an error while the request.  The
            request was not fully sent to the network.

          - WAITING: The request was fully sent to the network.  The
            instance is now waiting for the response to be fully received.

          - ABORTING: Application code has requested that the HTTP connection
            be aborted.

          - CONNECTION_LOST: The connection has been lost.

    @ivar _abortDeferreds: A list of C{Deferred} instances that will fire when
        the connection is lost.
    """
    _state = 'QUIESCENT'
    _parser = None
    _finishedRequest = None
    _currentRequest = None
    _transportProxy = None
    _responseDeferred = None


    def __init__(self, quiescentCallback=lambda c: None):
        self._quiescentCallback = quiescentCallback
        self._abortDeferreds = []


    @property
    def state(self):
        return self._state


    def request(self, request):
        """
        Issue C{request} over C{self.transport} and return a L{Deferred} which
        will fire with a L{Response} instance or an error.

        @param request: The object defining the parameters of the request to
           issue.
        @type request: L{Request}

        @rtype: L{Deferred}
        @return: The deferred may errback with L{RequestGenerationFailed} if
            the request was not fully written to the transport due to a local
            error.  It may errback with L{RequestTransmissionFailed} if it was
            not fully written to the transport due to a network error.  It may
            errback with L{ResponseFailed} if the request was sent (not
            necessarily received) but some or all of the response was lost.  It
            may errback with L{RequestNotSent} if it is not possible to send
            any more requests using this L{HTTP11ClientProtocol}.
        """
        if self._state != 'QUIESCENT':
            return fail(RequestNotSent())

        self._state = 'TRANSMITTING'
        _requestDeferred = maybeDeferred(request.writeTo, self.transport)

        def cancelRequest(ign):
            # Explicitly cancel the request's deferred if it's still trying to
            # write when this request is cancelled.
            if self._state in (
                    'TRANSMITTING', 'TRANSMITTING_AFTER_RECEIVING_RESPONSE'):
                _requestDeferred.cancel()
            else:
                self.transport.abortConnection()
                self._disconnectParser(Failure(CancelledError()))
        self._finishedRequest = Deferred(cancelRequest)

        # Keep track of the Request object in case we need to call stopWriting
        # on it.
        self._currentRequest = request

        self._transportProxy = TransportProxyProducer(self.transport)
        self._parser = HTTPClientParser(request, self._finishResponse)
        self._parser.makeConnection(self._transportProxy)
        self._responseDeferred = self._parser._responseDeferred

        def cbRequestWrotten(ignored):
            if self._state == 'TRANSMITTING':
                self._state = 'WAITING'
                self._responseDeferred.chainDeferred(self._finishedRequest)

        def ebRequestWriting(err):
            if self._state == 'TRANSMITTING':
                self._state = 'GENERATION_FAILED'
                self.transport.abortConnection()
                self._finishedRequest.errback(
                    Failure(RequestGenerationFailed([err])))
            else:
                log.err(err, 'Error writing request, but not in valid state '
                             'to finalize request: %s' % self._state)

        _requestDeferred.addCallbacks(cbRequestWrotten, ebRequestWriting)

        return self._finishedRequest


    def _finishResponse(self, rest):
        """
        Called by an L{HTTPClientParser} to indicate that it has parsed a
        complete response.

        @param rest: A C{str} giving any trailing bytes which were given to
            the L{HTTPClientParser} which were not part of the response it
            was parsing.
        """
    _finishResponse = makeStatefulDispatcher('finishResponse', _finishResponse)


    def _finishResponse_WAITING(self, rest):
        # Currently the rest parameter is ignored. Don't forget to use it if
        # we ever add support for pipelining. And maybe check what trailers
        # mean.
        if self._state == 'WAITING':
            self._state = 'QUIESCENT'
        else:
            # The server sent the entire response before we could send the
            # whole request.  That sucks.  Oh well.  Fire the request()
            # Deferred with the response.  But first, make sure that if the
            # request does ever finish being written that it won't try to fire
            # that Deferred.
            self._state = 'TRANSMITTING_AFTER_RECEIVING_RESPONSE'
            self._responseDeferred.chainDeferred(self._finishedRequest)

        # This will happen if we're being called due to connection being lost;
        # if so, no need to disconnect parser again, or to call
        # _quiescentCallback.
        if self._parser is None:
            return

        reason = ConnectionDone("synthetic!")
        connHeaders = self._parser.connHeaders.getRawHeaders('connection', ())
        if (('close' in connHeaders) or self._state != "QUIESCENT" or
            not self._currentRequest.persistent):
            self._giveUp(Failure(reason))
        else:
            # We call the quiescent callback first, to ensure connection gets
            # added back to connection pool before we finish the request.
            try:
                self._quiescentCallback(self)
            except:
                # If callback throws exception, just log it and disconnect;
                # keeping persistent connections around is an optimisation:
                log.err()
                self.transport.loseConnection()
            self._disconnectParser(reason)


    _finishResponse_TRANSMITTING = _finishResponse_WAITING


    def _disconnectParser(self, reason):
        """
        If there is still a parser, call its C{connectionLost} method with the
        given reason.  If there is not, do nothing.

        @type reason: L{Failure}
        """
        if self._parser is not None:
            parser = self._parser
            self._parser = None
            self._currentRequest = None
            self._finishedRequest = None
            self._responseDeferred = None

            # The parser is no longer allowed to do anything to the real
            # transport.  Stop proxying from the parser's transport to the real
            # transport before telling the parser it's done so that it can't do
            # anything.
            self._transportProxy._stopProxying()
            self._transportProxy = None
            parser.connectionLost(reason)


    def _giveUp(self, reason):
        """
        Lose the underlying connection and disconnect the parser with the given
        L{Failure}.

        Use this method instead of calling the transport's loseConnection
        method directly otherwise random things will break.
        """
        self.transport.loseConnection()
        self._disconnectParser(reason)


    def dataReceived(self, bytes):
        """
        Handle some stuff from some place.
        """
        try:
            self._parser.dataReceived(bytes)
        except:
            self._giveUp(Failure())


    def connectionLost(self, reason):
        """
        The underlying transport went away.  If appropriate, notify the parser
        object.
        """
    connectionLost = makeStatefulDispatcher('connectionLost', connectionLost)


    def _connectionLost_QUIESCENT(self, reason):
        """
        Nothing is currently happening.  Move to the C{'CONNECTION_LOST'}
        state but otherwise do nothing.
        """
        self._state = 'CONNECTION_LOST'


    def _connectionLost_GENERATION_FAILED(self, reason):
        """
        The connection was in an inconsistent state.  Move to the
        C{'CONNECTION_LOST'} state but otherwise do nothing.
        """
        self._state = 'CONNECTION_LOST'


    def _connectionLost_TRANSMITTING(self, reason):
        """
        Fail the L{Deferred} for the current request, notify the request
        object that it does not need to continue transmitting itself, and
        move to the C{'CONNECTION_LOST'} state.
        """
        self._state = 'CONNECTION_LOST'
        self._finishedRequest.errback(
            Failure(RequestTransmissionFailed([reason])))
        del self._finishedRequest

        # Tell the request that it should stop bothering now.
        self._currentRequest.stopWriting()


    def _connectionLost_TRANSMITTING_AFTER_RECEIVING_RESPONSE(self, reason):
        """
        Move to the C{'CONNECTION_LOST'} state.
        """
        self._state = 'CONNECTION_LOST'


    def _connectionLost_WAITING(self, reason):
        """
        Disconnect the response parser so that it can propagate the event as
        necessary (for example, to call an application protocol's
        C{connectionLost} method, or to fail a request L{Deferred}) and move
        to the C{'CONNECTION_LOST'} state.
        """
        self._disconnectParser(reason)
        self._state = 'CONNECTION_LOST'


    def _connectionLost_ABORTING(self, reason):
        """
        Disconnect the response parser with a L{ConnectionAborted} failure, and
        move to the C{'CONNECTION_LOST'} state.
        """
        self._disconnectParser(Failure(ConnectionAborted()))
        self._state = 'CONNECTION_LOST'
        for d in self._abortDeferreds:
            d.callback(None)
        self._abortDeferreds = []


    def abort(self):
        """
        Close the connection and cause all outstanding L{request} L{Deferred}s
        to fire with an error.
        """
        if self._state == "CONNECTION_LOST":
            return succeed(None)
        self.transport.loseConnection()
        self._state = 'ABORTING'
        d = Deferred()
        self._abortDeferreds.append(d)
        return d
