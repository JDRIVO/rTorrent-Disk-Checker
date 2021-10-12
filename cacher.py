import os
import time
import logging
import config as cfg
from threading import Thread
from datetime import datetime
from utils import sortTorrents
from remote_caller import SCGIRequest

try:
	from importlib import reload
except:
	from imp import reload


class Cache(SCGIRequest):

	def __init__(self):
		super(Cache, self).__init__()
		self.torrents, self.mountPoints, self.torrentsDownloading, self.pendingDeletions = {}, {}, {}, {}
		self.deletions, self.pending = [], []
		self.lock = self.refreshing = self.repeat = False
		self.lastModified = 0

		self.getMountPoints()
		self.refreshTorrents()
		Thread(target=self.getTorrents).start()
		Thread(target=self.removeTorrents).start()

	def reloadConfig(self):
		lastModified = os.path.getmtime("config.py")

		if lastModified > self.lastModified:
			self.lastModified = lastModified

			try:
				reload(cfg)
			except Exception as e:
				logging.error("cacher.py: Config Error: Couldn't reload config: " + str(e))

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

				Thread(target=self.removeTorrent, args=(torrentHash, mountPoint)).start()

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

			while cfg.enable_cache:

				while self.lock or self.deletions or self.pending:
					time.sleep(60)

				self.refreshTorrents()
				time.sleep(cfg.cache_interval)

			self.reloadConfig()
			time.sleep(1)

	def refreshTorrents(self):
		self.reloadConfig()

		while self.deletions or self.pending:
			time.sleep(0.01)

		self.refreshing = True

		try:
			completedTorrents = self.send(
				"d.multicall2",
				(
					"",
					"complete",
					"d.hash=",
					"d.name=",
					"d.directory=",
					"d.custom1=",
					"t.multicall=,t.url=",
					"d.timestamp.finished=",
					"d.ratio=",
					"t.multicall=,t.url=,t.scrape_complete=",
					"d.size_bytes=",
				),
			)
			torrentsDownloading = self.send("d.multicall2", ("", "leeching", "d.hash="))
			stoppedTorrents = self.send("d.multicall2", ("", "stopped", "d.hash=", "d.complete="))
		except:
			self.refreshing = False
			return True

		completedTorrents = [
			(
				tPath.rsplit("/", 1)[0] if tName in tPath else tPath,
				tHash,
				tLabel,
				tTracker,
				(datetime.now() - datetime.utcfromtimestamp(tAge)).days,
				tRatio / 1000.0,
				max([seeds[1] for seeds in tSeeders]),
				tSize,
				tSize / 1073741824.0,
			)
			for tHash, tName, tPath, tLabel, tTracker, tAge, tRatio, tSeeders, tSize in completedTorrents
		]
		sortedTorrents = sortTorrents(cfg.sort_order, cfg.group_order, completedTorrents)
		torrents, torrentHashes = {}, {}

		for torrentData in sortedTorrents:
			parentDirectory, torrentHash = torrentData[:2]
			torrentData = torrentData[1:]
			torrentHashes[torrentHash] = torrentData
			mountPoint = self.mountPoints[parentDirectory] if parentDirectory in self.mountPoints else self.getMountPoint(parentDirectory)

			if mountPoint in torrents:
				torrents[mountPoint].append(torrentData)
			else:
				torrents[mountPoint] = [torrentData]

		while (self.lock and cfg.enable_cache and not self.repeat) or self.deletions or self.pending:

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

			time.sleep(0.01)

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
			[torrentHash, torrentPath.rsplit("/", 1)[0] if torrentName in torrentPath else torrentPath]
			for torrentHash, torrentName, torrentPath in torrentsDownloading
		] + [
			[torrentHash, torrentPath.rsplit("/", 1)[0] if torrentName in torrentPath else torrentPath]
			for complete, torrentHash, torrentName, torrentPath in stoppedTorrents
			if not complete
		]

		for torrentName, torrentPath in completedTorrents:
			parentDirectory = torrentPath.rsplit("/", 1)[0] if torrentName in torrentPath else torrentPath

			if parentDirectory not in self.mountPoints:
				self.getMountPoint(parentDirectory)

		for torrentHash, parentDirectory in incompleteTorrents:

			if parentDirectory not in self.mountPoints:
				mountPoint = self.getMountPoint(parentDirectory)
			else:
				mountPoint = self.mountPoints[parentDirectory]

			try:
				self.torrentsDownloading[mountPoint].append(torrentHash)
			except:
				self.torrentsDownloading[mountPoint] = [torrentHash]
