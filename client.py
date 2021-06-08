import socket
import sys
import config as cfg

torrent_magnet = sys.argv[1]
torrent_name = sys.argv[2]
torrent_label = sys.argv[3]
torrent_hash = sys.argv[4]
torrent_path = sys.argv[5]
torrent_size = int(sys.argv[6]) / 1073741824.0

if torrent_magnet:
	from remote_caller import SCGIRequest
	rtxmlrpc = SCGIRequest()
	rtxmlrpc.send('d.start', (torrent_hash,) )
else:
	headerSize = 10

	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(cfg.socket_file)

	message = f"{torrent_magnet}, {torrent_name}, {torrent_label}, {torrent_hash}, {torrent_path}, {torrent_size}"
	message = bytes(f"{len(message):<{headerSize}}" + message, "utf-8")
	s.send(message)
