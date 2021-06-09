import sys

torrent_magnet = int(sys.argv[1])
torrent_name = sys.argv[2]
torrent_label = sys.argv[3]
torrent_hash = sys.argv[4]
torrent_path = sys.argv[5]
torrent_size = int(sys.argv[6]) / 1073741824.0

error = False

if torrent_magnet:

	try:
		from remote_caller import SCGIRequest
		rtxmlrpc = SCGIRequest()
		rtxmlrpc.send('d.start', (torrent_hash,) )
	except Exception as e:
		error = f"XMLRPC Error: Couldn't add torrent: {torrent_name}: " + str(e)

else:

	try:
		import socket
		import config as cfg

		headerSize = 10

		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		s.connect(cfg.socket_file)

		message = f"{torrent_name}, {torrent_label}, {torrent_hash}, {torrent_path}, {torrent_size}"
		message = bytes(f"{len(message):<{headerSize}}" + message, "utf-8")
		s.send(message)

	except Exception as e:
		error = f"Server Error: Couldn't process torrent: {torrent_name}: " + str(e)

if error:
	import logging
	logging.basicConfig(filename='client.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
	logging.critical(error)