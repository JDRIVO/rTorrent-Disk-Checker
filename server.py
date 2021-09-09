import os
import sys
import socket
import logging
import subprocess
from threading import Thread
from queuer import CheckerQueue
from cacher import Cache

logging.basicConfig(filename="checker_server.log", level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")

try:
	import config as cfg
except Exception as e:
	print(e)
	logging.critical("server.py: Config Error: Couldn't import socket_file:", e)
	sys.exit(1)

cmd = "pgrep -a python | grep " + sys.argv[0]
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pid, err = process.communicate()

if len(pid.splitlines()) > 1:
	print("Server is already running in the background. If you are updating, kill the server process and try again.")
	sys.exit(0)

if "/" not in sys.argv[0]:
	from remote_caller import SCGIRequest
	rtxmlrpc = SCGIRequest()
	print("Server is now running in the background.")
	rtxmlrpc.send("execute.throw.bg", ("", "python3", os.path.join(os.path.abspath(os.getcwd()), sys.argv[0])))
	sys.exit(0)

cache = Cache()
checkerQueue = CheckerQueue()
checkerQueue.createChecker(cache)

socketFile = cfg.socket_file
if os.path.exists(socketFile): os.remove(socketFile)

try:
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.bind(socketFile)
	s.listen(50)

	while True:
		clientsocket, address = s.accept()
		message = clientsocket.recv(2048).decode("utf-8").split("|:|")

		if "delete" in message:
			cache.hashes.append(message)
		else:
			checkerQueue.put(message)

except Exception as e:
	print(e)
	logging.critical("server.py: Server Error: Server closing:", e)
