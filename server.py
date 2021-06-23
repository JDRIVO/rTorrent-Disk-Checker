import logging
logging.basicConfig(filename="server.log", level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")

import socket
import os
import sys
import subprocess
from threading import Thread
from cacher import Cache
import queuer

cmd = "pgrep -a python | grep " + sys.argv[0]
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pid, err = process.communicate()

if len(pid.splitlines() ) > 1:
	sys.exit(0)

try:
	import config as cfg
except Exception as e:
	logging.critical("server.py: Config Error: Couldn't import socket_file: " + str(e) )
	sys.exit(1)

cache = Cache()
t = Thread(target=cache.getTorrents)
t.start()
cache.getMountPoints()

checkerQueue = queuer.CheckerQueue()
deleterQueue = queuer.DeleterQueue()

checkerQueue.createChecker(cache, deleterQueue)
deleterQueue.createDeleter(cache)

t = Thread(target=deleterQueue.processor)
t.setDaemon(True)
t.start()
t = Thread(target=checkerQueue.processor)
t.setDaemon(True)
t.start()

socketFile = cfg.socket_file
if os.path.exists(socketFile): os.remove(socketFile)

try:
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.bind(socketFile)
	s.listen(50)

	while True:
		clientsocket, address = s.accept()
		message = clientsocket.recv(2048)
		checkerQueue.queueAdd(message.decode("utf-8").split("|:|") )

except Exception as e:
	logging.critical("server.py: Server Error: Server closing: " + str(e) )