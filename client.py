import sys
import socket

try:
	import config as cfg
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(cfg.socket_file)
	data = "|:|".join(sys.argv).encode("utf-8")
	s.send(data)
except Exception as e:
	import os
	import logging

	os.chdir(os.path.dirname(sys.argv[0]))
	logging.basicConfig(filename="diskchecker.log", level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
	logging.critical("client.py: Couldn't process torrent: {}: {}".format(sys.argv[1], e))
