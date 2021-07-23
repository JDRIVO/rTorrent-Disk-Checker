import os
import time
import logging
from threading import Thread
from datetime import datetime
from remote_caller import SCGIRequest
from messenger import message
from deleter import Deleter

try:
	from importlib import reload
except:
	from imp import reload

try:
	import config as cfg
except Exception as e:
	logging.critical("checker.py: Config Error: Couldn't import config file:", e)


class Checker(SCGIRequest):

	def __init__(self, cache, checkerQueue):
		super(Checker, self).__init__()
		self.cache = cache
		self.checkerQueue = checkerQueue
		deleter = Deleter(self.cache)
		self.delete = deleter.deletions

		self.mountPoints = self.cache.mountPoints
		self.torrentsDownloading = self.cache.torrentsDownloading
		self.pendingDeletions = self.cache.pendingDeletions
		self.labelRules, self.trackerRules, self.trackers = {}, {}, {}
		self.lastModified = 0

		self.include = True
		self.exclude = self.no = False
		self.whitelist = "whitelist"
		self.blacklist = "blacklist"

	def addRules(self, mode, dic):

		if self.include in mode:

			for title in mode[self.include]:
				dic[title] = self.include

		if self.exclude in mode:

			for title in mode[self.exclude]:
				dic[title] = self.exclude

		for title, rules in mode.items():

			if title not in (self.include, self.exclude):
				dic[title] = rules

	def check(self, torrentData):
		torrentName, torrentHash, torrentPath, torrentSize = torrentData[1:]
		torrentSize = int(torrentSize) / 1073741824.0
		lastModified = os.path.getmtime("config.py")

		if lastModified > self.lastModified:

			try:
				reload(cfg)
			except Exception as e:
				self.cache.lock = False
				self.checkerQueue.release = True
				logging.critical("checker.py: {}: Config Error: Couldn't import config file: {}".format(torrentName, e) )
				return

			self.lastModified = lastModified
			self.labelRules, self.trackerRules, self.trackers = {}, {}, {}
			self.addRules(cfg.labels, self.labelRules)
			self.addRules(cfg.trackers, self.trackerRules)

		completedTorrents = self.cache.torrents
		completedTorrentsCopy = completedTorrents[:]
		parentDirectory = torrentPath.rsplit('/', 1)[0] if torrentName in torrentPath else torrentPath

		try:
			mountPoint = self.mountPoints[parentDirectory]
		except:
			mountPoint = [path for path in [parentDirectory.rsplit('/', n)[0] for n in range(parentDirectory.count('/') )] if os.path.ismount(path)]
			mountPoint = mountPoint[0] if mountPoint else '/'
			self.mountPoints[parentDirectory] = mountPoint

		try:
			downloads = self.torrentsDownloading[mountPoint]

			if downloads:

				try:
					downloading = self.send("d.multicall2", ('', "leeching", "d.left_bytes=", "d.hash=") )
					downloading = sum(tBytes for tBytes, tHash in downloading if tHash in downloads)
				except Exception as e:
					self.cache.lock = False
					self.checkerQueue.release = True
					logging.critical("checker.py: {}: XMLRPC Error: Couldn't retrieve torrents: {}".format(torrentName, e) )
					return

			else:
				downloading = 0

			downloads.append(torrentHash)

		except:
			self.torrentsDownloading[mountPoint] = [torrentHash]
			downloading = 0

		try:
			deletions = self.pendingDeletions[mountPoint]
		except:
			deletions = self.pendingDeletions[mountPoint] = 0

		disk = os.statvfs(mountPoint)
		availableSpace = (disk.f_bsize * disk.f_bavail + deletions - downloading) / 1073741824.0
		minimumSpace = cfg.minimum_space_mp[mountPoint] if mountPoint in cfg.minimum_space_mp else cfg.minimum_space
		requiredSpace = torrentSize - (availableSpace - minimumSpace)
		requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_mode, cfg.fallback_size, cfg.fallback_age, cfg.fallback_ratio

		freedSpace = 0
		override = True
		fallbackTorrents = []
		currentTime = datetime.now()

		while freedSpace < requiredSpace and (completedTorrentsCopy or fallbackTorrents):

			if completedTorrentsCopy:
				torrent = completedTorrentsCopy.pop(0)
				tLabel, tTracker, tHash, tPath, tSizeBytes, tSizeGigabytes, tRatio, tAge, parentDirectory = torrent

				if override:
					override = False
					minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = requirements

				if cfg.exclude_unlabelled and not tLabel:
					continue

				if self.labelRules:

					if tLabel in self.labelRules:
						labelRule = self.labelRules[tLabel]

						if labelRule is self.exclude:
							continue

						if labelRule is not self.include:

							if self.blacklist in labelRule:

								try:
									tracker = self.trackers[tLabel + tTracker[0][0]]
								except:
									tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

									for url in tTracker:
										self.trackers[tLabel + url[0]] = tracker

								if tracker:
									continue

							elif self.whitelist in labelRule:

								try:
									tracker = self.trackers[tLabel + tTracker[0][0]]
								except:
									tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

									for url in tTracker:
										self.trackers[tLabel + url[0]] = tracker

								if not tracker:
									continue

							if labelRule[0] is not self.include:
								override = True
								minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = labelRule[:7]

					elif cfg.labels_only:
						continue

				if self.trackerRules and not override:

					try:
						tracker = self.trackers[tTracker[0][0]]
					except:
						tracker = [tracker for tracker in self.trackerRules for url in tTracker if tracker in url[0]]

						for url in tTracker:
							self.trackers[url[0]] = tracker

					if tracker:
						trackerRule = self.trackerRules[tracker[0]]

						if trackerRule is self.exclude:
							continue

						if trackerRule is not self.include:
							override = True
							minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = trackerRule

					elif cfg.trackers_only:
						continue

				tAgeDays = (currentTime - tAge).days

				if tSizeGigabytes < minSize or tRatio < minRatio or tAgeDays < minAge:

					if fbMode == 1:

						if tSizeGigabytes < fbSize or tRatio < fbRatio or tAgeDays < fbAge:
							continue
						else:
							fallbackTorrents.append(torrent)

					elif fbMode == 2:

						if (
								fbSize is not self.no and tSizeGigabytes >= fbSize) or (
								fbRatio is not self.no and tRatio >= fbRatio) or (
								fbAge is not self.no and tAgeDays >= fbAge):
							fallbackTorrents.append(torrent)

					continue

			else:
				torrent = fallbackTorrents.pop(0)
				tLabel, tTracker, tHash, tPath, tSizeBytes, tSizeGigabytes, tRatio, tAge, parentDirectory = torrent

			if self.mountPoints[parentDirectory] != mountPoint:
				continue

			try:
				completedTorrents.remove(torrent)
			except:
				continue

			self.delete.append( (tHash, tSizeBytes, tPath, mountPoint) )
			self.pendingDeletions[mountPoint] += tSizeBytes
			freedSpace += tSizeGigabytes

		self.cache.lock = False
		self.checkerQueue.release = True

		if freedSpace >= requiredSpace:

			try:
				self.send("d.start", (torrentHash,) )
			except Exception as e:
				logging.error("checker.py: {}: XMLRPC Error: Couldn't start torrent: {}".format(torrentName, e) )

		elif freedSpace < requiredSpace and (cfg.enable_email or cfg.enable_pushbullet or cfg.enable_telegram or cfg.enable_slack):

			try:
				message()
			except Exception as e:
				logging.error("checker.py: Message Error: Couldn't send message:", e)
