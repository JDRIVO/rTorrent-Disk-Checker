from config import scgi

try:
        import xmlrpc.client as xmlrpclib, socket
        python3 = True
except:
        import xmlrpclib, socket
        python3 = False

class SCGIRequest(object):

        def __init__(self, url):
                self.url = url

        def __send(self, scgireq):
                ip = self.url.split(':')
                host = ip[0]
                port = ip[1]
                addrinfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
                sock = socket.socket(*addrinfo[0][:3])
                sock.connect(addrinfo[0][4])
                sock.send(scgireq.encode())

                if python3:
                        recvdata = resp = sock.recv(1024).decode(errors='ignore')
                else:
                        recvdata = resp = sock.recv(1024)

                while recvdata != '':

                        if python3:
                                recvdata = sock.recv(1024).decode(errors='ignore')
                        else:
                                recvdata = sock.recv(1024)

                        resp += recvdata

                sock.close()
                return resp

        def send(self, data):
                "Send data over scgi to url and get response"
                scgiresp = self.__send(self.add_required_scgi_headers(data))
                resp = ''.join(scgiresp.split('\n')[4:])
                return resp

        @staticmethod
        def encode_netstring(string):
                "Encode string as netstring"
                return '%d:%s,' % (len(string), string)

        @staticmethod
        def make_headers(headers):
                "Make scgi header list"
                return '\x00'.join(['%s\x00%s' % t for t in headers]) + '\x00'

        @staticmethod
        def add_required_scgi_headers(data, headers = []):
                "Wrap data in an scgi request,\nsee spec at: http://python.ca/scgi/protocol.txt"
                headers = SCGIRequest.make_headers([('CONTENT_LENGTH', str(len(data))), ('SCGI', '1'),] + headers)
                enc_headers = SCGIRequest.encode_netstring(headers)
                return enc_headers + data

def xmlrpc(methodname, params):
        xmlreq = xmlrpclib.dumps(params, methodname)
        xmlresp = SCGIRequest(scgi).send(xmlreq)
        return xmlrpclib.loads(xmlresp)[0][0]
