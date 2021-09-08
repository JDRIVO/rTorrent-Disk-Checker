import sys
import socket

try:
	import config as cfg
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(cfg.socket_file)
	message = "|:|".join(sys.argv).encode("utf-8")
	s.send(message)
except Exception as e:
	import os
	import logging
	logging.basicConfig(filename="checker_client.log", level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
	logging.critical("Server Error: Couldn't process torrent: {}: {}".format(sys.argv[1], e))
