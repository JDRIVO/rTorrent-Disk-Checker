import sys
import socket

torrentName = sys.argv[1]
torrentHash = sys.argv[2]
torrentPath = sys.argv[3]
torrentSize = sys.argv[4]

try:
	import config as cfg
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(cfg.socket_file)

	message = ", ".join( (torrentName, torrentHash, torrentPath, torrentSize) )
	message = "{:<10}{}".format(len(message), message).encode("utf-8")
	s.send(message)
except Exception as e:
	import logging
	logging.basicConfig(filename="client.log", level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
	logging.critical("Server Error: Couldn't process torrent: {}: {}".format(torrentName, e) )