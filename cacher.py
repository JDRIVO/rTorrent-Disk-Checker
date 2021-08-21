import os
import time
import logging
import itertools
from threading import Thread
from datetime import datetime
from remote_caller import SCGIRequest

try:
	from importlib import reload
except:
	from imp import reload

try:
	import config as cfg
except Exception as e:
	logging.critical("cacher.py: Config Error: Setting cache_interval to default value of 300:", e)


class Cache(SCGIRequest):

	def __init__(self):
		super(Cache, self).__init__()
		self.pendingDeletions, self.torrentsDownloading, self.mountPoints = {}, {}, {}
		self.deletions, self.pending = [], []
		self.torrents = None
		self.lock = False
		t = Thread(target=self.getTorrents)
		t.start()
		t = Thread(target=self.removeTorrents)
		t.start()

	def removeTorrents(self):
		self.hashes = []

		while True:

			while self.hashes:

				try:
					tHash = self.hashes.pop(0)[2]
					self.torrents.remove(self.torrentsDic[tHash])
				except:
					continue

			time.sleep(0.01)

	def getTorrents(self):

		while True:

			while self.lock or self.deletions or self.pending:
				time.sleep(60)

			try:
				torrents = self.send(
					"d.multicall2",
					('',
					"complete",
					"d.timestamp.finished=",
					"d.ratio=",
					"d.name=",
					"d.custom1=",
					"t.multicall=,t.url=",
					"d.hash=",
					"d.directory=",
					"d.size_bytes=") )
			except:
				time.sleep(60)
				continue

			torrents.sort()
			self.torrents = [tData[3:] + [tData[-1] / 1073741824.0, tData[1] / 1000.0, datetime.utcfromtimestamp(tData[0]),
					tData[6].rsplit('/', 1)[0] if tData[2] in tData[6] else tData[6]] for tData in torrents]
			self.torrentsDic = {tData[2]: tData for tData in self.torrents}
			downloading = [tHash[0] for tHash in self.send("d.multicall2", ('', "leeching", "d.hash=") )] + \
			[tHash for tHash, complete in self.send("d.multicall2", ('', "stopped", "d.hash=", "d.complete=") ) if complete == 0]
			[tHashes.remove(tHash) for tHashes in self.torrentsDownloading.values() for tHash in tHashes[:] if tHash not in downloading]

			try:
				reload(cfg)
				interval = cfg.cache_interval
			except Exception as e:
				logging.critical("cacher.py: Config Error: Setting cache_interval to default value of 300:", e)
				interval = 300

			time.sleep(interval)

	def getMountPoints(self):

		def getMountPoint(parentDirectory):
			mountPoint = [path for path in [parentDirectory.rsplit('/', n)[0] for n in range(parentDirectory.count('/') )] if os.path.ismount(path)]
			mountPoint = mountPoint[0] if mountPoint else '/'
			self.mountPoints[parentDirectory] = mountPoint
			return mountPoint

		downloading = self.send("d.multicall2", ('', "leeching", "d.hash=", "d.name=", "d.directory=") )
		stopped = self.send("d.multicall2", ('', "stopped", "d.complete=", "d.hash=", "d.name=", "d.directory=") )
		incompleteTorrents = [[tHash, tPath.rsplit('/', 1)[0] if tName in tPath else tPath] for tHash, tName, tPath in downloading] + \
		[[tHash, tPath.rsplit('/', 1)[0] if tName in tPath else tPath] for complete, tHash, tName, tPath in stopped if complete == 0]

		while not self.torrents:
			time.sleep(1)

		for torrentData, incompleteTorrentData in itertools.zip_longest(self.torrents, incompleteTorrents):

			if torrentData:
				getMountPoint(torrentData[-1])

			if incompleteTorrentData:
				mountPoint = getMountPoint(incompleteTorrentData[-1])

				try:
					self.torrentsDownloading[mountPoint].append(incompleteTorrentData[0])
				except:
					self.torrentsDownloading[mountPoint] = [incompleteTorrentData[0]]
