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
    IReactorUDP, IReactorMulticast, IReactorProcess,
    IReactorTime, IDelayedCall, IReactorThreads, IReactorCore,
    IReactorPluggableResolver, IReactorFDSet,
    IListeningPort, ILoggingContext, IFileDescriptor, IReadDescriptor,
    IWriteDescriptor, IReadWriteDescriptor, IHalfCloseableDescriptor,
    ISystemHandle, IConsumer, IProducer, IPushProducer, IPullProducer,
    IProtocol, IProcessProtocol, IHalfCloseableProtocol,
    IProtocolFactory, ITransport, IProcessTransport, IServiceCollection,
    IUDPTransport, IUNIXDatagramTransport, IUNIXDatagramConnectedTransport,
    IMulticastTransport,
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



class IReactorWin32Events(Interface):
    """
    Win32 Event API methods

    @since: 10.2
    """

    def addEvent(event, fd, action):
        """
        Add a new win32 event to the event loop.

        @param event: a Win32 event object created using win32event.CreateEvent()

        @param fd: an instance of L{twisted.internet.abstract.FileDescriptor}

        @param action: a string that is a method name of the fd instance.
                       This method is called in response to the event.

        @return: None
        """


    def removeEvent(event):
        """
        Remove an event.

        @param event: a Win32 event object added using L{IReactorWin32Events.addEvent}

        @return: None
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



class IReactorDaemonize(Interface):
    """
    A reactor which provides hooks that need to be called before and after
    daemonization.

    Notes:
       - This interface SHOULD NOT be called by applications.
       - This interface should only be implemented by reactors as a workaround
         (in particular, it's implemented currently only by kqueue()).
         For details please see the comments on ticket #1918.
    """

    def beforeDaemonize():
        """
        Hook to be called immediately before daemonization. No reactor methods
        may be called until L{afterDaemonize} is called.

        @return: C{None}.
        """


    def afterDaemonize():
        """
        Hook to be called immediately after daemonization. This may only be
        called after L{beforeDaemonize} had been called previously.

        @return: C{None}.
        """



class IFileDescriptorReceiver(Interface):
    """
    Protocols may implement L{IFileDescriptorReceiver} to receive file
    descriptors sent to them.  This is useful in conjunction with
    L{IUNIXTransport}, which allows file descriptors to be sent between
    processes on a single host.
    """
    def fileDescriptorReceived(descriptor):
        """
        Called when a file descriptor is received over the connection.

        @param descriptor: The descriptor which was received.
        @type descriptor: C{int}

        @return: C{None}
        """



class ITCPTransport(ITransport):
    """
    A TCP based transport.
    """

    def loseWriteConnection():
        """
        Half-close the write side of a TCP connection.

        If the protocol instance this is attached to provides
        IHalfCloseableProtocol, it will get notified when the operation is
        done. When closing write connection, as with loseConnection this will
        only happen when buffer has emptied and there is no registered
        producer.
        """


    def abortConnection():
        """
        Close the connection abruptly.

        Discards any buffered data, stops any registered producer,
        and, if possible, notifies the other end of the unclean
        closure.

        @since: 11.1
        """


    def getTcpNoDelay():
        """
        Return if C{TCP_NODELAY} is enabled.
        """

    def setTcpNoDelay(enabled):
        """
        Enable/disable C{TCP_NODELAY}.

        Enabling C{TCP_NODELAY} turns off Nagle's algorithm. Small packets are
        sent sooner, possibly at the expense of overall throughput.
        """

    def getTcpKeepAlive():
        """
        Return if C{SO_KEEPALIVE} is enabled.
        """

    def setTcpKeepAlive(enabled):
        """
        Enable/disable C{SO_KEEPALIVE}.

        Enabling C{SO_KEEPALIVE} sends packets periodically when the connection
        is otherwise idle, usually once every two hours. They are intended
        to allow detection of lost peers in a non-infinite amount of time.
        """

    def getHost():
        """
        Returns L{IPv4Address} or L{IPv6Address}.
        """

    def getPeer():
        """
        Returns L{IPv4Address} or L{IPv6Address}.
        """



class IUNIXTransport(ITransport):
    """
    Transport for stream-oriented unix domain connections.
    """
    def sendFileDescriptor(descriptor):
        """
        Send a duplicate of this (file, socket, pipe, etc) descriptor to the
        other end of this connection.

        The send is non-blocking and will be queued if it cannot be performed
        immediately.  The send will be processed in order with respect to other
        C{sendFileDescriptor} calls on this transport, but not necessarily with
        respect to C{write} calls on this transport.  The send can only be
        processed if there are also bytes in the normal connection-oriented send
        buffer (ie, you must call C{write} at least as many times as you call
        C{sendFileDescriptor}).

        @param descriptor: An C{int} giving a valid file descriptor in this
            process.  Note that a I{file descriptor} may actually refer to a
            socket, a pipe, or anything else POSIX tries to treat in the same
            way as a file.

        @return: C{None}
        """



class ITLSTransport(ITCPTransport):
    """
    A TCP transport that supports switching to TLS midstream.

    Once TLS mode is started the transport will implement L{ISSLTransport}.
    """

    def startTLS(contextFactory):
        """
        Initiate TLS negotiation.

        @param contextFactory: A context factory (see L{ssl.py<twisted.internet.ssl>})
        """

class ISSLTransport(ITCPTransport):
    """
    A SSL/TLS based transport.
    """

    def getPeerCertificate():
        """
        Return an object with the peer's certificate info.
        """


class IStreamClientEndpoint(Interface):
    """
    A stream client endpoint is a place that L{ClientFactory} can connect to.
    For example, a remote TCP host/port pair would be a TCP client endpoint.

    @since: 10.1
    """

    def connect(protocolFactory):
        """
        Connect the C{protocolFactory} to the location specified by this
        L{IStreamClientEndpoint} provider.

        @param protocolFactory: A provider of L{IProtocolFactory}
        @return: A L{Deferred} that results in an L{IProtocol} upon successful
            connection otherwise a L{ConnectError}
        """



class IStreamServerEndpoint(Interface):
    """
    A stream server endpoint is a place that a L{Factory} can listen for
    incoming connections.

    @since: 10.1
    """

    def listen(protocolFactory):
        """
        Listen with C{protocolFactory} at the location specified by this
        L{IStreamServerEndpoint} provider.

        @param protocolFactory: A provider of L{IProtocolFactory}
        @return: A L{Deferred} that results in an L{IListeningPort} or an
            L{CannotListenError}
        """



class IStreamServerEndpointStringParser(Interface):
    """
    An L{IStreamServerEndpointStringParser} is like an
    L{IStreamClientEndpointStringParser}, except for L{IStreamServerEndpoint}s
    instead of clients.  It integrates with L{endpoints.serverFromString} in
    much the same way.
    """

    prefix = Attribute(
        """
        @see: L{IStreamClientEndpointStringParser.prefix}
        """
    )


    def parseStreamServer(reactor, *args, **kwargs):
        """
        Parse a stream server endpoint from a reactor and string-only arguments
        and keyword arguments.

        @see: L{IStreamClientEndpointStringParser.parseStreamClient}

        @return: a stream server endpoint
        @rtype: L{IStreamServerEndpoint}
        """



class IStreamClientEndpointStringParser(Interface):
    """
    An L{IStreamClientEndpointStringParser} is a parser which can convert
    a set of string C{*args} and C{**kwargs} into an L{IStreamClientEndpoint}
    provider.

    This interface is really only useful in the context of the plugin system
    for L{endpoints.clientFromString}.  See the document entitled "I{The
    Twisted Plugin System}" for more details on how to write a plugin.

    If you place an L{IStreamClientEndpointStringParser} plugin in the
    C{twisted.plugins} package, that plugin's C{parseStreamClient} method will
    be used to produce endpoints for any description string that begins with
    the result of that L{IStreamClientEndpointStringParser}'s prefix attribute.
    """

    prefix = Attribute(
        """
        A C{str}, the description prefix to respond to.  For example, an
        L{IStreamClientEndpointStringParser} plugin which had C{"foo"} for its
        C{prefix} attribute would be called for endpoint descriptions like
        C{"foo:bar:baz"} or C{"foo:"}.
        """
    )


    def parseStreamClient(*args, **kwargs):
        """
        This method is invoked by L{endpoints.clientFromString}, if the type of
        endpoint matches the return value from this
        L{IStreamClientEndpointStringParser}'s C{prefix} method.

        @param args: The string arguments, minus the endpoint type, in the
            endpoint description string, parsed according to the rules
            described in L{endpoints.quoteStringArgument}.  For example, if the
            description were C{"my-type:foo:bar:baz=qux"}, C{args} would be
            C{('foo','bar')}

        @param kwargs: The string arguments from the endpoint description
            passed as keyword arguments.  For example, if the description were
            C{"my-type:foo:bar:baz=qux"}, C{kwargs} would be
            C{dict(baz='qux')}.

        @return: a client endpoint
        @rtype: L{IStreamClientEndpoint}
        """
