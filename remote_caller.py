import socket
import xmlrpc.client as xmlrpclib
from urllib import parse as urllib
from config import scgi

class SCGIRequest(object):

		def __init__(self):
			self.url = scgi

		def send(self, methodname, params):
			"Send data over scgi to url and get response"
			data = xmlrpclib.dumps(params, methodname)
			scgiresp = self.__send(self.addRequiredSCGIHeaders(data) )
			xmlresp = ''.join(scgiresp.split("\n")[4:])
			return xmlrpclib.loads(xmlresp)[0][0]

		def __send(self, scgireq):

			try:
				host, port = self.url.split(":")
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
		def encodeNetstring(string):
			"Encode string as netstring"
			return "%d:%s," % (len(string), string)

		@staticmethod
		def makeHeaders(headers):
			"Make scgi header list"
			return "\x00".join(["%s\x00%s" % t for t in headers]) + "\x00"

		@staticmethod
		def addRequiredSCGIHeaders(data, headers = []):
			"Wrap data in an scgi request, see spec at: http://python.ca/scgi/protocol.txt"
			headers = SCGIRequest.makeHeaders([("CONTENT_LENGTH", str(len(data) ) ), ("SCGI", "1"),] + headers)
			encHeaders = SCGIRequest.encodeNetstring(headers)
			return encHeaders + data