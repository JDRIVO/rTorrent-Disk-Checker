from config import scgi

try:
		import xmlrpclib, socket
		import urllib
except:
		import xmlrpc.client as xmlrpclib, socket
		from urllib import parse as urllib

class SCGIRequest:

		def __init__(self):
			self.url = scgi

		def send(self, methodname, params):
			"Send data over scgi to url and get response"
			data = xmlrpclib.dumps(params, methodname)
			scgiresp = self.__send(self.add_required_scgi_headers(data) )
			xmlresp = ''.join(scgiresp.split('\n')[4:])
			return xmlrpclib.loads(xmlresp)[0][0]

		def __send(self, scgireq):

			try:
				host, port = self.url.split(':')
				addrinfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
				sock = socket.socket(*addrinfo[0][:3])
				sock.connect(addrinfo[0][4])
			except:
				sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
				sock.connect(self.url)

			sock.send(scgireq.encode() )
			sfile = sock.makefile()
			response = ''

			while True:
				data = sfile.read(1024)

				if not data:
					break

				response += data

			sock.close()
			return urllib.unquote(response)

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
			headers = SCGIRequest.make_headers([('CONTENT_LENGTH', str(len(data) ) ), ('SCGI', '1'),] + headers)
			enc_headers = SCGIRequest.encode_netstring(headers)
			return enc_headers + data