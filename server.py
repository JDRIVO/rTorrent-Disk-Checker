import logging
logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

import socket
import time
import os
import sys
from threading import Thread
from cacher import Cache
import queuer

try:
	import config as cfg
except Exception as e:
	logging.critical(f"server.py: Config Error: Couldn't import socket_file: {e}")
	sys.exit(1)

socketFile = cfg.socket_file
if os.path.exists(socketFile): os.remove(socketFile)

checkerQueue = queuer.CheckerQueue()
deleterQueue = queuer.DeleterQueue()

cache = Cache()
t = Thread(target=cache.getTorrents)
t.start()
cache.getMountPoints()

checkerQueue.createChecker(cache, deleterQueue)
deleterQueue.createDeleter(cache)

t = Thread(target=deleterQueue.processor)
t.setDaemon(True)
t.start()
t = Thread(target=checkerQueue.processor)
t.setDaemon(True)
t.start()

headerSize = 10

try:
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.bind(socketFile)
	s.listen(50)

	while True:
		completeMessage = b''
		newMessage = True
		clientsocket, address = s.accept()

		while True:
			message = clientsocket.recv(1024)

			if newMessage:
				messageLength = int(message[:headerSize])
				newMessage = False

			completeMessage += message

			if len(completeMessage) - headerSize == messageLength:
				checkerQueue.queueAdd(completeMessage[headerSize:].decode('utf-8').split(', ') )
				break

except Exception as e:
	logging.critical(f"server.py: Server Error: Server closing: {e}")