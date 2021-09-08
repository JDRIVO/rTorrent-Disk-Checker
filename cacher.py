import os
import time
import logging
from threading import Thread
from datetime import datetime
from utils import sortTorrents
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
				completedTorrents = self.send(
					"d.multicall2",
					(
						"",
						"complete",
						"d.name=",
						"d.hash=",
						"d.custom1=",
						"t.multicall=,t.url=",
						"d.timestamp.finished=",
						"t.multicall=,t.url=,t.scrape_complete=",
						"d.ratio=",
						"d.size_bytes=",
						"d.directory=",
					),
				)
				downloading = self.send("d.multicall2", ("", "leeching", "d.hash="))
				downloadingStopped = self.send("d.multicall2", ("", "stopped", "d.hash=", "d.complete="))
			except:
				time.sleep(60)
				continue

			completedTorrents = [
				(
					(datetime.now() - datetime.utcfromtimestamp(tAge)).days,
					tName,
					tHash,
					tLabel,
					tTracker,
					datetime.utcfromtimestamp(tAge),
					max(seeds[1] for seeds in tSeeders),
					tRatio / 1000.0,
					tSize,
					tSize / 1073741824.0,
					tPath,
					tPath.rsplit("/", 1)[0] if tName in tPath else tPath,
				)
				for tName, tHash, tLabel, tTracker, tAge, tSeeders, tRatio, tSize, tPath in completedTorrents
			]
			self.torrents = sortTorrents(cfg.sort_order, cfg.group_order, completedTorrents)
			self.torrentsDic = {tData[2]: tData for tData in self.torrents}
			downloading = [tHash[0] for tHash in downloading] + [tHash for tHash, complete in downloadingStopped if not complete]
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
			mountPoint = [path for path in [parentDirectory.rsplit("/", n)[0] for n in range(parentDirectory.count("/"))] if os.path.ismount(path)]
			mountPoint = mountPoint[0] if mountPoint else "/"
			self.mountPoints[parentDirectory] = mountPoint
			return mountPoint

		while True:

			try:
				downloading = self.send("d.multicall2", ("", "leeching", "d.hash=", "d.name=", "d.directory="))
				downloadingStopped = self.send("d.multicall2", ("", "stopped", "d.complete=", "d.hash=", "d.name=", "d.directory="))
				break
			except:
				time.sleep(1)

		incompleteTorrents = [
			[tHash, tPath.rsplit("/", 1)[0] if tName in tPath else tPath]
			for tHash, tName, tPath in downloading
		] + [
			[tHash, tPath.rsplit("/", 1)[0] if tName in tPath else tPath]
			for complete, tHash, tName, tPath in downloadingStopped
			if not complete
		]

		while not self.torrents:
			time.sleep(1)

		for torrentData in self.torrents:
			parentDirectory = torrentData[-1]

			if parentDirectory not in self.mountPoints:
				getMountPoint(parentDirectory)

		for torrentData in incompleteTorrents:
			parentDirectory = torrentData[-1]

			if parentDirectory not in self.mountPoints:
				mountPoint = getMountPoint(parentDirectory)
			else:
				mountPoint = self.mountPoints[parentDirectory]

			try:
				self.torrentsDownloading[mountPoint].append(torrentData[0])
			except:
				self.torrentsDownloading[mountPoint] = [torrentData[0]]
