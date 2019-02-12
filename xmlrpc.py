import xmlrpclib, urllib, urlparse, socket, cStringIO as StringIO
from config import host

def xmlrpc(methodname, params):
        xmlreq = xmlrpclib.dumps(params, methodname)
        xmlresp = SCGIRequest(host).send(xmlreq)
        return xmlrpclib.loads(xmlresp)[0][0]

class SCGIRequest(object):

        def __init__(self, url):
                self.url = url
                self.resp_headers = []

        def __send(self, scgireq):
                scheme, netloc, path, query, frag = urlparse.urlsplit(self.url)
                host, port = urllib.splitport(netloc)

                if netloc:
                        inet6_host = ''

                        if len(inet6_host) > 0:
                                addrinfo = socket.getaddrinfo(inet6_host, port, socket.AF_INET6, socket.SOCK_STREAM)
                        else:
                                addrinfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)

                        assert len(addrinfo) == 1, "There's more than one? %r" % addrinfo

                        sock = socket.socket(*addrinfo[0][:3])
                        sock.connect(addrinfo[0][4])
                else:
                        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        sock.connect(path)

                sock.send(scgireq)
                recvdata = resp = sock.recv(1024)

                while recvdata != '':
                        recvdata = sock.recv(1024)
                        resp += recvdata

                sock.close()
                return resp

        def send(self, data):
                "Send data over scgi to url and get response"
                scgiresp = self.__send(self.add_required_scgi_headers(data))
                resp, self.resp_headers = self.get_scgi_resp(scgiresp)
                return resp

        @staticmethod
        def encode_netstring(string):
                "Encode string as netstring"
                return '%d:%s,'%(len(string), string)

        @staticmethod
        def make_headers(headers):
                "Make scgi header list"
                return '\x00'.join(['%s\x00%s'%t for t in headers])+'\x00'

        @staticmethod
        def add_required_scgi_headers(data, headers = []):
                "Wrap data in an scgi request,\nsee spec at: http://python.ca/scgi/protocol.txt"
                headers = SCGIRequest.make_headers([('CONTENT_LENGTH', str(len(data))),('SCGI', '1'),] + headers)
                enc_headers = SCGIRequest.encode_netstring(headers)
                return enc_headers+data

        @staticmethod
        def gen_headers(file):
                "Get header lines from scgi response"
                line = file.readline().rstrip()

                while line.strip():
                        yield line
                        line = file.readline().rstrip()

        @staticmethod
        def get_scgi_resp(resp):
                "Get xmlrpc response from scgi response"
                fresp = StringIO.StringIO(resp)
                headers = []

                for line in SCGIRequest.gen_headers(fresp):
                        headers.append(line.split(': ', 1))

                xmlresp = fresp.read()
                return (xmlresp, headers)
