import socket
from xmlrpc import client as xmlrpclib
from urllib import parse as urllib
from config import scgi


class SCGIRequest:

	def __init__(self):
		self.url = scgi

	def send(self, methodName, params):
		data = xmlrpclib.dumps(params, methodName)
		scgiResp = self.__send(self.addRequiredSCGIHeaders(data))
		xmlResp = "".join(scgiResp.split("\n")[4:])
		return xmlrpclib.loads(xmlResp)[0][0]

	def __send(self, scgiReq):

		try:
			host, port = self.url.split(":")
			addrInfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
			sock = socket.socket(*addrInfo[0][:3])
			sock.connect(addrInfo[0][4])
		except:
			sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			sock.connect(self.url)

		sock.send(scgiReq.encode())
		sFile = sock.makefile()
		resp = ""

		while True:
			data = sFile.read(1024)

			if not data:
				break

			resp += data

		sock.close()
		return urllib.unquote(resp)

	@staticmethod
	def encodeNetstring(string):
		return "%d:%s," % (len(string), string)

	@staticmethod
	def makeHeaders(headers):
		return "\x00".join(["%s\x00%s" % t for t in headers]) + "\x00"

	@staticmethod
	def addRequiredSCGIHeaders(data):
		headers = SCGIRequest.makeHeaders([("CONTENT_LENGTH", str(len(data))), ("SCGI", "1")])
		encHeaders = SCGIRequest.encodeNetstring(headers)
		return encHeaders + data
