import sys

torrentMagnet = int(sys.argv[1])
torrentName = sys.argv[2]
torrentLabel = sys.argv[3]
torrentHash = sys.argv[4]
torrentPath = sys.argv[5]
torrentSize = int(sys.argv[6]) / 1073741824.0

error = False

if torrentMagnet:

	try:
		from remote_caller import SCGIRequest
		rtxmlrpc = SCGIRequest()
		rtxmlrpc.send('d.start', (torrentHash,) )
	except Exception as e:
		error = f"XMLRPC Error: Couldn't add torrent: {torrentName}: {e}"

else:

	try:
		import socket
		import config as cfg

		headerSize = 10

		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		s.connect(cfg.socket_file)

		message = f"{torrentName}, {torrentLabel}, {torrentHash}, {torrentPath}, {torrentSize}"
		message = bytes(f"{len(message):<{headerSize}}" + message, "utf-8")
		s.send(message)

	except Exception as e:
		error = f"Server Error: Couldn't process torrent: {torrentName}: {e}"

if error:
	import logging
	logging.basicConfig(filename='client.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
	logging.critical(error)