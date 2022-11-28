import socket
from xmlrpc import client as xmlrpclib
from urllib import parse as urllib

from config import scgi


class SCGIRequest:

	def __init__(self):

		try:
			host, port = scgi.split(":")
			addrInfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
			self.sInfo = addrInfo[0][:3]
			self.scgi = addrInfo[0][4]
		except:
			self.sInfo = socket.AF_UNIX, socket.SOCK_STREAM
			self.scgi = scgi

	def send(self, methodName, params):
		xmlRequest = xmlrpclib.dumps(params, methodName)
		scgiRequest = self.addHeaders(xmlRequest).encode("utf-8")

		s = socket.socket(*self.sInfo)
		s.connect(self.scgi)
		s.send(scgiRequest)

		sFile = s.makefile()
		data = response = sFile.read(1024)

		while data:
			data = sFile.read(1024)
			response += data

		s.close()

		scgiResponse = urllib.unquote(response)
		xmlResponse = "".join(scgiResponse.split("\n")[4:])
		return xmlrpclib.loads(xmlResponse)[0][0]

	@staticmethod
	def addHeaders(body):
		headers = "CONTENT_LENGTH\x00{}\x00SCGI1\x00".format(len(body))
		encodedHeaders = "{}:{},".format(len(headers), headers)
		return encodedHeaders + body
