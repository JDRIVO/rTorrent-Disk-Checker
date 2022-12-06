import os
import sys
import signal
import socket
import logging
import subprocess

script = sys.argv[0]

if "/" in script:
	os.chdir(os.path.dirname(script))

logging.basicConfig(filename="diskchecker.log", level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")

try:
	import config as cfg
except Exception as e:
	print("Error: Couldn't import config file:", e)
	logging.critical("server.py: Config Error: Couldn't import config file: " + str(e))
	sys.exit(1)

from queuer import CheckerQueue
from checker import Checker
from cacher import Cache

serverPath = os.path.join(os.path.abspath(os.getcwd()), script)
cmd = "pgrep -a python | grep " + script
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pids = process.communicate()[0].splitlines()

if len(pids) > 1:
	myPid = os.getpid()
	[os.kill(int(pid.split()[0]), signal.SIGKILL) for pid in pids if serverPath in str(pid) and int(pid.split()[0]) != myPid]

if "/" not in script:
	print("Disk checker (server.py) is now running in the background.")
	subprocess.Popen([sys.executable, serverPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	sys.exit(0)

cache = Cache()
checker = Checker(cache)
checkerQueue = CheckerQueue(cache, checker)

socketFile = cfg.socket_file

if os.path.exists(socketFile):
	os.remove(socketFile)

try:
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.bind(socketFile)
	s.listen(50)

	while True:
		clientSocket, address = s.accept()
		data = clientSocket.recv(2048).decode("utf-8").split("|:|")

		if "delete" in data:
			cache.deletedTorrents.append(data)
		else:
			checkerQueue.put(data)

except Exception as e:
	print(e)
	logging.critical("server.py: Server Error: Server closing: " + str(e))
