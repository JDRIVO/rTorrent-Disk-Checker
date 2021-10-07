import socket
from xmlrpc import client as xmlrpclib
from urllib import parse as urllib
from config import scgi


class SCGIRequest:

	def __init__(self):

		if ":" in scgi:
			host, port = scgi.split(":")
			addrInfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
			self.sInfo = addrInfo[0][:3]
			self.scgi = addrInfo[0][4]
		else:
			self.sInfo = socket.AF_UNIX, socket.SOCK_STREAM
			self.scgi = scgi

	def send(self, methodName, params):
		xmlReq = xmlrpclib.dumps(params, methodName)
		scgiReq = self.addSCGIHeaders(xmlReq).encode("utf-8")

		s = socket.socket(*self.sInfo)
		s.connect(self.scgi)
		s.send(scgiReq)

		sFile = s.makefile()
		data = resp = sFile.read(1024)

		while data:
			data = sFile.read(1024)
			resp += data

		s.close()

		scgiResp = urllib.unquote(resp)
		xmlResp = "".join(scgiResp.split("\n")[4:])
		return xmlrpclib.loads(xmlResp)[0][0]

	@staticmethod
	def encodeNetstring(string):
		return "%d:%s," % (len(string), string)

	@staticmethod
	def makeHeaders(headers):
		return "\x00".join(["%s\x00%s" % h for h in headers]) + "\x00"

	@staticmethod
	def addSCGIHeaders(data):
		headers = SCGIRequest.makeHeaders([("CONTENT_LENGTH", str(len(data))), ("SCGI", "1")])
		encHeaders = SCGIRequest.encodeNetstring(headers)
		return encHeaders + data
