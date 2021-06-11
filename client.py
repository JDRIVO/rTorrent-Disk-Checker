import sys
import socket

torrentName = sys.argv[1]
torrentHash = sys.argv[2]
torrentPath = sys.argv[3]
torrentSize = int(sys.argv[4]) / 1073741824.0

try:
	import config as cfg

	headerSize = 10

	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(cfg.socket_file)

	message = f"{torrentName}, {torrentHash}, {torrentPath}, {torrentSize}"
	message = bytes(f"{len(message):<{headerSize}}" + message, "utf-8")
	s.send(message)
except Exception as e:
	import logging
	logging.basicConfig(filename='client.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
	logging.critical(f"Server Error: Couldn't process torrent: {torrentName}: {e}")
