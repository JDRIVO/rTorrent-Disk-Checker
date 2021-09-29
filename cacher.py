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
		self.torrents, self.mountPoints, self.torrentsDownloading, self.pendingDeletions = {}, {}, {}, {}
		self.deletions, self.pending = [], []
		self.lock = self.refreshing = False
		self.getMountPoints()
		self.refreshTorrents()
		t = Thread(target=self.getTorrents)
		t.start()
		t = Thread(target=self.removeTorrents)
		t.start()

	def removeTorrents(self):
		self.deletedTorrents = []

		while True:

			while self.deletedTorrents:
				torrentHash, torrentName, torrentPath = self.deletedTorrents.pop(0)[2:]
				parentDirectory = torrentPath.rsplit("/", 1)[0] if torrentName in torrentPath else torrentPath
				mountPoint = self.mountPoints[parentDirectory] if parentDirectory in self.mountPoints else self.getMountPoint(parentDirectory)

				try:
					self.torrents[mountPoint].remove(self.torrentHashes[torrentHash])
				except:
					pass

				t = Thread(target=self.removeTorrent, args=(torrentHash, mountPoint))
				t.start()

			time.sleep(0.01)

	def removeTorrent(self, torrentHash, mountPoint):

		while self.refreshing:
			time.sleep(0.01)

		try:
			self.torrents[mountPoint].remove(self.torrentHashes[torrentHash])
		except:
			pass

	def updatePending(self, torrentData):

		while self.refreshing:
			time.sleep(0.01)

		try:
			self.pending.remove(torrentData)
		except:
			pass

	def getTorrents(self):

		while True:

			while self.lock or self.deletions or self.pending:
				time.sleep(60)

			if cfg.enable_cache:
				self.refreshTorrents()

			try:
				reload(cfg)
				interval = cfg.cache_interval
			except Exception as e:
				logging.critical("cacher.py: Config Error: Setting cache_interval to default value of 300:", e)
				interval = 300

			time.sleep(interval)

	def refreshTorrents(self):

		while self.deletions or self.pending:
			time.sleep(0.1)

		self.refreshing = True

		try:
			completedTorrents = self.send(
				"d.multicall2",
				(
					"",
					"complete",
					"d.name=",
					"d.directory=",
					"d.hash=",
					"d.timestamp.finished=",
					"d.custom1=",
					"t.multicall=,t.url=",
					"t.multicall=,t.url=,t.scrape_complete=",
					"d.ratio=",
					"d.size_bytes=",
				),
			)
			torrentsDownloading = self.send("d.multicall2", ("", "leeching", "d.hash="))
			stoppedTorrents = self.send("d.multicall2", ("", "stopped", "d.hash=", "d.complete="))
		except:
			self.refreshing = False
			return

		completedTorrents = [
			(
				tName,
				tPath,
				tHash,
				(datetime.now() - datetime.utcfromtimestamp(tAge)).days,
				tLabel,
				tTracker,
				max([seeds[1] for seeds in tSeeders]),
				tRatio / 1000.0,
				tSize,
				tSize / 1073741824.0,
			)
			for tName, tPath, tHash, tAge, tLabel, tTracker, tSeeders, tRatio, tSize in completedTorrents
		]
		sortedTorrents = sortTorrents(cfg.sort_order, cfg.group_order, completedTorrents)
		torrents, torrentHashes = {}, {}

		for torrentData in sortedTorrents:
			tName, tPath, tHash = torrentData[:3]
			torrentData = torrentData[2:]
			torrentHashes[tHash] = torrentData
			parentDirectory = tPath.rsplit("/", 1)[0] if tName in tPath else tPath
			mountPoint = self.mountPoints[parentDirectory] if parentDirectory in self.mountPoints else self.getMountPoint(parentDirectory)

			if mountPoint in torrents:
				torrents[mountPoint].append(torrentData)
			else:
				torrents[mountPoint] = [torrentData]

		if self.deletions or self.pending or self.pendingDeletions:

			while self.deletions:

				try:
					torrentHash, mountPoint, torrentSize = self.deletions[0]
					torrents[mountPoint].remove(torrentHashes[torrentHash])
				except:
					pass

			while self.pending:

				try:
					torrentHash, mountPoint, torrentSize = self.pending.pop(0)
					torrents[mountPoint].remove(torrentHashes[torrentHash])
				except:
					pass

		self.torrents = torrents
		self.torrentHashes = torrentHashes
		self.refreshing = False
		torrentsDownloading = [tHash[0] for tHash in torrentsDownloading] + [tHash for tHash, complete in stoppedTorrents if not complete]
		[tHashes.remove(tHash) for tHashes in self.torrentsDownloading.values() for tHash in tHashes[:] if tHash not in torrentsDownloading]

	def getMountPoint(self, parentDirectory):
		mountPoint = [path for path in [parentDirectory.rsplit("/", n)[0] for n in range(parentDirectory.count("/"))] if os.path.ismount(path)]
		mountPoint = mountPoint[0] if mountPoint else "/"
		self.mountPoints[parentDirectory] = mountPoint
		return mountPoint

	def getMountPoints(self):

		while True:

			try:
				completedTorrents = self.send("d.multicall2", ("", "complete", "d.name=", "d.directory="))
				torrentsDownloading = self.send("d.multicall2", ("", "leeching", "d.hash=", "d.name=", "d.directory="))
				stoppedTorrents = self.send("d.multicall2", ("", "stopped", "d.complete=", "d.hash=", "d.name=", "d.directory="))
				break
			except:
				time.sleep(1)

		incompleteTorrents = [
			[tHash, tPath.rsplit("/", 1)[0] if tName in tPath else tPath]
			for tHash, tName, tPath in torrentsDownloading
		] + [
			[tHash, tPath.rsplit("/", 1)[0] if tName in tPath else tPath]
			for complete, tHash, tName, tPath in stoppedTorrents
			if not complete
		]

		for tName, tPath in completedTorrents:
			parentDirectory = tPath.rsplit("/", 1)[0] if tName in tPath else tPath

			if parentDirectory not in self.mountPoints:
				self.getMountPoint(parentDirectory)

		for torrentData in incompleteTorrents:
			parentDirectory = torrentData[-1]

			if parentDirectory not in self.mountPoints:
				mountPoint = self.getMountPoint(parentDirectory)
			else:
				mountPoint = self.mountPoints[parentDirectory]

			try:
				self.torrentsDownloading[mountPoint].append(torrentData[0])
			except:
				self.torrentsDownloading[mountPoint] = [torrentData[0]]
