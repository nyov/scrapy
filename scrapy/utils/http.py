"""
Transitional module for moving to the w3lib library.

For new code, always import from w3lib.http instead of this module
"""

from w3lib.http import *

def decode_chunked_transfer(chunked_body):
    """Parsed body received with chunked transfer encoding, and return the
    decoded body.

    For more info see:
    https://en.wikipedia.org/wiki/Chunked_transfer_encoding

    """
    body, h, t = '', '', chunked_body
    while t:
        h, t = t.split('\r\n', 1)
        if h == '0':
            break
        size = int(h, 16)
        body += t[:size]
        t = t[size+2:]
    return body


# Patch urllib.proxy_bypass function to correctly understand
# `no_proxy`/$NO_PROXY ENV variable on *NIX environments.
import sys, os
import socket

#from requests.utils import address_in_network, is_ipv4_address, is_valid_cidr
import struct

def address_in_network(ip, net):
    """
    This function allows you to check if on IP belongs to a network subnet
    Example: returns True if ip = 192.168.1.1 and net = 192.168.1.0/24
             returns False if ip = 192.168.1.1 and net = 192.168.100.0/24
    """
    ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
    netaddr, bits = net.split('/')
    netmask = struct.unpack('=L', socket.inet_aton(dotted_netmask(int(bits))))[0]
    network = struct.unpack('=L', socket.inet_aton(netaddr))[0] & netmask
    return (ipaddr & netmask) == (network & netmask)

def is_ipv4_address(string_ip):
    try:
        socket.inet_aton(string_ip)
    except socket.error:
        return False
    return True

def is_valid_cidr(string_network):
    """Very simple check of the cidr format in no_proxy variable"""
    if string_network.count('/') == 1:
        try:
            mask = int(string_network.split('/')[1])
        except ValueError:
            return False

        if mask < 1 or mask > 32:
            return False

        try:
            socket.inet_aton(string_network.split('/')[0])
        except socket.error:
            return False
    else:
        return False
    return True


# `urllib.proxy_bypass_environment` fails to recognize
# IPs or CIDR notation in $NO_PROXY env variable
def proxy_bypass_environment(netloc):
    """Test if proxies should not be used for a particular host.
    """
    get_proxy = lambda k: os.environ.get(k) or os.environ.get(k.upper())
    no_proxy = get_proxy('no_proxy')

    if no_proxy:
        # '*' is special case for always bypass
        if no_proxy == '*':
            return 1

        no_proxy_list = no_proxy.replace(' ', '').split(',')

        host = netloc.split(':')[0]
        # check if this is an IP or CIDR notation
        if is_ipv4_address(host):
            for proxy_ip in no_proxy:
                if is_valid_cidr(proxy_ip):
                    if address_in_network(host, proxy_ip):
                        return 1
        else:
            # check if the host ends with any of the DNS suffixes
            for proxyhost in no_proxy_list:
                if proxyhost and \
                        (host.endswith(proxyhost) or netloc.endswith(proxyhost)):
                    return 1

    # otherwise, don't bypass
    return 0

if sys.platform != 'darwin' and os.name != 'nt':
    proxy_bypass = proxy_bypass_environment
