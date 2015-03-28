import sys, os
import socket
import base64
from six.moves.urllib.request import getproxies, proxy_bypass
from six.moves.urllib.parse import unquote
try:
    from urllib2 import _parse_proxy
except ImportError:
    from urllib.request import _parse_proxy
from six.moves.urllib.parse import urlunparse

from scrapy.utils.httpobj import urlparse_cached
from scrapy.exceptions import NotConfigured
from scrapy.utils.python import to_bytes

try:
    from requests.utils import address_in_network, is_ipv4_address, is_valid_cidr
except ImportError:

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


# urllib.proxy_bypass_environment fails to recognize
# IPs or CIDR notation in $NO_PROXY env
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


class HttpProxyMiddleware(object):

    def __init__(self, auth_encoding='latin-1'):
        self.auth_encoding = auth_encoding
        self.proxies = {}
        for type, url in getproxies().items():
            self.proxies[type] = self._get_proxy(url, type)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING')
        return cls(auth_encoding)

    def _basic_auth_header(self, username, password):
        user_pass = to_bytes(
            '%s:%s' % (unquote(username), unquote(password)),
            encoding=self.auth_encoding)
        return base64.b64encode(user_pass).strip()

    def _get_proxy(self, url, orig_type):
        proxy_type, user, password, hostport = _parse_proxy(url)
        proxy_url = urlunparse((proxy_type or orig_type, hostport, '', '', '', ''))

        if user:
            creds = self._basic_auth_header(user, password)
        else:
            creds = None

        return creds, proxy_url

    def process_request(self, request, spider):
        # ignore if proxy is already set
        if 'proxy' in request.meta:
            if request.meta['proxy'] is None:
                return
            # extract credentials if present
            creds, proxy_url = self._get_proxy(request.meta['proxy'], '')
            request.meta['proxy'] = proxy_url
            if creds and not request.headers.get('Proxy-Authorization'):
                request.headers['Proxy-Authorization'] = b'Basic ' + creds
            return
        elif not self.proxies:
            return

        parsed = urlparse_cached(request)
        scheme = parsed.scheme

        # 'no_proxy' is only supported by http schemes
        if scheme in ('http', 'https') and proxy_bypass(parsed.netloc):
            return

        if scheme in self.proxies:
            self._set_proxy(request, scheme)

    def _set_proxy(self, request, scheme):
        creds, proxy = self.proxies[scheme]
        request.meta['proxy'] = proxy
        if creds:
            request.headers['Proxy-Authorization'] = b'Basic ' + creds
