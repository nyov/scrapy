# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Interface documentation.

Maintainer: Itamar Shtull-Trauring
"""

from __future__ import division, absolute_import

from zope.interface import Interface, Attribute

from twisted.internet.interfaces import (
    IAddress, IConnector, IResolverSimple, IReactorTCP, IReactorSSL,
    IReactorWin32Events, IReactorUDP, IReactorMulticast, IReactorProcess,
    IReactorTime, IDelayedCall, IReactorThreads, IReactorCore,
    IReactorPluggableResolver, IReactorDaemonize, IReactorFDSet,
    IListeningPort, ILoggingContext, IFileDescriptor, IReadDescriptor,
    IWriteDescriptor, IReadWriteDescriptor, IHalfCloseableDescriptor,
    ISystemHandle, IConsumer, IProducer, IPushProducer, IPullProducer,
    IProtocol, IProcessProtocol, IHalfCloseableProtocol,
    IFileDescriptorReceiver, IProtocolFactory, ITransport, ITCPTransport,
    IUNIXTransport,
    ITLSTransport, ISSLTransport, IProcessTransport, IServiceCollection,
    IUDPTransport, IUNIXDatagramTransport, IUNIXDatagramConnectedTransport,
    IMulticastTransport, IStreamClientEndpoint, IStreamServerEndpoint,
    IStreamServerEndpointStringParser, IStreamClientEndpointStringParser,
)


class IResolver(IResolverSimple):
    def query(query, timeout=None):
        """
        Dispatch C{query} to the method which can handle its type.

        @type query: L{twisted.names.dns.Query}
        @param query: The DNS query being issued, to which a response is to be
            generated.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupAddress(name, timeout=None):
        """
        Perform an A record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupAddress6(name, timeout=None):
        """
        Perform an A6 record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupIPV6Address(name, timeout=None):
        """
        Perform an AAAA record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupMailExchange(name, timeout=None):
        """
        Perform an MX record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupNameservers(name, timeout=None):
        """
        Perform an NS record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupCanonicalName(name, timeout=None):
        """
        Perform a CNAME record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupMailBox(name, timeout=None):
        """
        Perform an MB record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupMailGroup(name, timeout=None):
        """
        Perform an MG record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupMailRename(name, timeout=None):
        """
        Perform an MR record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupPointer(name, timeout=None):
        """
        Perform a PTR record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupAuthority(name, timeout=None):
        """
        Perform an SOA record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupNull(name, timeout=None):
        """
        Perform a NULL record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupWellKnownServices(name, timeout=None):
        """
        Perform a WKS record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupHostInfo(name, timeout=None):
        """
        Perform a HINFO record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupMailboxInfo(name, timeout=None):
        """
        Perform an MINFO record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupText(name, timeout=None):
        """
        Perform a TXT record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupResponsibility(name, timeout=None):
        """
        Perform an RP record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupAFSDatabase(name, timeout=None):
        """
        Perform an AFSDB record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupService(name, timeout=None):
        """
        Perform an SRV record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupAllRecords(name, timeout=None):
        """
        Perform an ALL_RECORD lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupSenderPolicy(name, timeout= 10):
        """
        Perform a SPF record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupNamingAuthorityPointer(name, timeout=None):
        """
        Perform a NAPTR record lookup.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: Sequence of C{int}
        @param timeout: Number of seconds after which to reissue the query.
            When the last timeout expires, the query is considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.  The first element of the
            tuple gives answers.  The second element of the tuple gives
            authorities.  The third element of the tuple gives additional
            information.  The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """


    def lookupZone(name, timeout=None):
        """
        Perform an AXFR record lookup.

        NB This is quite different from other DNS requests. See
        U{http://cr.yp.to/djbdns/axfr-notes.html} for more
        information.

        NB Unlike other C{lookup*} methods, the timeout here is not a
        list of ints, it is a single int.

        @type name: C{str}
        @param name: DNS name to resolve.

        @type timeout: C{int}
        @param timeout: When this timeout expires, the query is
            considered failed.

        @rtype: L{Deferred}
        @return: A L{Deferred} which fires with a three-tuple of lists of
            L{twisted.names.dns.RRHeader} instances.
            The first element of the tuple gives answers.
            The second and third elements are always empty.
            The L{Deferred} may instead fail with one of the
            exceptions defined in L{twisted.names.error} or with
            C{NotImplementedError}.
        """



class IReactorUNIX(Interface):
    """
    UNIX socket methods.
    """

    def connectUNIX(address, factory, timeout=30, checkPID=0):
        """
        Connect a client protocol to a UNIX socket.

        @param address: a path to a unix socket on the filesystem.

        @param factory: a L{twisted.internet.protocol.ClientFactory} instance

        @param timeout: number of seconds to wait before assuming the connection
            has failed.

        @param checkPID: if True, check for a pid file to verify that a server
            is listening.  If C{address} is a Linux abstract namespace path,
            this must be C{False}.

        @return: An object which provides L{IConnector}.
        """


    def listenUNIX(address, factory, backlog=50, mode=0o666, wantPID=0):
        """
        Listen on a UNIX socket.

        @param address: a path to a unix socket on the filesystem.

        @param factory: a L{twisted.internet.protocol.Factory} instance.

        @param backlog: number of connections to allow in backlog.

        @param mode: The mode (B{not} umask) to set on the unix socket.  See
            platform specific documentation for information about how this
            might affect connection attempts.
        @type mode: C{int}

        @param wantPID: if True, create a pidfile for the socket.  If C{address}
            is a Linux abstract namespace path, this must be C{False}.

        @return: An object which provides L{IListeningPort}.
        """



class IReactorUNIXDatagram(Interface):
    """
    Datagram UNIX socket methods.
    """

    def connectUNIXDatagram(address, protocol, maxPacketSize=8192, mode=0o666, bindAddress=None):
        """
        Connect a client protocol to a datagram UNIX socket.

        @param address: a path to a unix socket on the filesystem.

        @param protocol: a L{twisted.internet.protocol.ConnectedDatagramProtocol} instance

        @param maxPacketSize: maximum packet size to accept

        @param mode: The mode (B{not} umask) to set on the unix socket.  See
            platform specific documentation for information about how this
            might affect connection attempts.
        @type mode: C{int}

        @param bindAddress: address to bind to

        @return: An object which provides L{IConnector}.
        """


    def listenUNIXDatagram(address, protocol, maxPacketSize=8192, mode=0o666):
        """
        Listen on a datagram UNIX socket.

        @param address: a path to a unix socket on the filesystem.

        @param protocol: a L{twisted.internet.protocol.DatagramProtocol} instance.

        @param maxPacketSize: maximum packet size to accept

        @param mode: The mode (B{not} umask) to set on the unix socket.  See
            platform specific documentation for information about how this
            might affect connection attempts.
        @type mode: C{int}

        @return: An object which provides L{IListeningPort}.
        """



class IReactorSocket(Interface):
    """
    Methods which allow a reactor to use externally created sockets.

    For example, to use C{adoptStreamPort} to implement behavior equivalent
    to that of L{IReactorTCP.listenTCP}, you might write code like this::

        from socket import SOMAXCONN, AF_INET, SOCK_STREAM, socket
        portSocket = socket(AF_INET, SOCK_STREAM)
        # Set FD_CLOEXEC on port, left as an exercise.  Then make it into a
        # non-blocking listening port:
        portSocket.setblocking(False)
        portSocket.bind(('192.168.1.2', 12345))
        portSocket.listen(SOMAXCONN)

        # Now have the reactor use it as a TCP port
        port = reactor.adoptStreamPort(
            portSocket.fileno(), AF_INET, YourFactory())

        # portSocket itself is no longer necessary, and needs to be cleaned
        # up by us.
        portSocket.close()

        # Whenever the server is no longer needed, stop it as usual.
        stoppedDeferred = port.stopListening()

    Another potential use is to inherit a listening descriptor from a parent
    process (for example, systemd or launchd), or to receive one over a UNIX
    domain socket.

    Some plans for extending this interface exist.  See:

        - U{http://twistedmatrix.com/trac/ticket/5570}: established connections
        - U{http://twistedmatrix.com/trac/ticket/5573}: AF_UNIX ports
        - U{http://twistedmatrix.com/trac/ticket/5574}: SOCK_DGRAM sockets
    """

    def adoptStreamPort(fileDescriptor, addressFamily, factory):
        """
        Add an existing listening I{SOCK_STREAM} socket to the reactor to
        monitor for new connections to accept and handle.

        @param fileDescriptor: A file descriptor associated with a socket which
            is already bound to an address and marked as listening.  The socket
            must be set non-blocking.  Any additional flags (for example,
            close-on-exec) must also be set by application code.  Application
            code is responsible for closing the file descriptor, which may be
            done as soon as C{adoptStreamPort} returns.
        @type fileDescriptor: C{int}

        @param addressFamily: The address family (or I{domain}) of the socket.
            For example, L{socket.AF_INET6}.

        @param factory: A L{ServerFactory} instance to use to create new
            protocols to handle connections accepted via this socket.

        @return: An object providing L{IListeningPort}.

        @raise UnsupportedAddressFamily: If the given address family is not
            supported by this reactor, or not supported with the given socket
            type.

        @raise UnsupportedSocketType: If the given socket type is not supported
            by this reactor, or not supported with the given socket type.
        """


    def adoptStreamConnection(fileDescriptor, addressFamily, factory):
        """
        Add an existing connected I{SOCK_STREAM} socket to the reactor to
        monitor for data.

        Note that the given factory won't have its C{startFactory} and
        C{stopFactory} methods called, as there is no sensible time to call
        them in this situation.

        @param fileDescriptor: A file descriptor associated with a socket which
            is already connected.  The socket must be set non-blocking.  Any
            additional flags (for example, close-on-exec) must also be set by
            application code.  Application code is responsible for closing the
            file descriptor, which may be done as soon as
            C{adoptStreamConnection} returns.
        @type fileDescriptor: C{int}

        @param addressFamily: The address family (or I{domain}) of the socket.
            For example, L{socket.AF_INET6}.

        @param factory: A L{ServerFactory} instance to use to create a new
            protocol to handle the connection via this socket.

        @raise UnsupportedAddressFamily: If the given address family is not
            supported by this reactor, or not supported with the given socket
            type.

        @raise UnsupportedSocketType: If the given socket type is not supported
            by this reactor, or not supported with the given socket type.
        """

