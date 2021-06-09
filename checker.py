import sys
import os
import time
import importlib
import logging
from datetime import datetime
from threading import Thread
from remote_caller import SCGIRequest
from emailer import email
from deleter import Deleter

try:
	import config as cfg
except Exception as e:
	logging.critical(f"checker.py: Config Error: Couldn't import config file: {e}")

class Checker(SCGIRequest):

	def __init__(self, cache, checkerQueue, deleterQueue):
		super().__init__()
		self.cache = cache
		self.checkerQueue = checkerQueue
		self.deleter = Deleter(cache, deleterQueue)

	def	check(self, torrentInfo):
		self.cache.lock = True

		torrentName, torrentLabel, torrentHash, torrentPath, torrentSize = torrentInfo
		torrentSize = float(torrentSize)

		try:
			importlib.reload(cfg)
		except Exception as e:
			self.cache.lock = False
			self.checkerQueue.release = True
			logging.critical(f"checker.py: Config Error: Couldn't import config file: {torrentName}: {e}")
			return

		completedTorrents = self.cache.torrents
		torrentsDownloading = self.cache.torrentsDownloading
		pendingDeletions = self.cache.pendingDeletions
		mountPoints = self.cache.mountPoints
		parentDirectory = torrentPath.rsplit('/', 1)[0] if torrentName in torrentPath else torrentPath

		if parentDirectory in mountPoints:
			mountPoint = mountPoints[parentDirectory]
		else:
			mountPoint = [path for path in [parentDirectory.rsplit('/', num)[0] for num in range(parentDirectory.count('/') )] if os.path.ismount(path)]
			mountPoint = mountPoint[0] if mountPoint else '/'
			mountPoints[parentDirectory] = mountPoint

		if torrentsDownloading:

			try:
				downloading = self.send('d.multicall2', ('', 'leeching', 'd.left_bytes=', 'd.hash=') )
				downloading = sum(tBytes for tBytes, tHash in downloading if tHash != torrentHash and tHash in torrentsDownloading and torrentsDownloading[tHash] == mountPoint)
			except Exception as e:
				self.cache.lock = False
				self.checkerQueue.release = True
				logging.critical(f"checker.py: XMLRPC Error: Couldn't retrieve torrents: {torrentName}: {e}")
				return

		else:
			downloading = 0

		if mountPoint in pendingDeletions:
			unaccounted = pendingDeletions[mountPoint]
		else:
			unaccounted = pendingDeletions[mountPoint] = 0

		disk = os.statvfs(mountPoint)
		availableSpace = (disk.f_bsize * disk.f_bavail + unaccounted - downloading) / 1073741824.0
		minimumSpace = cfg.minimum_space_mp[mountPoint] if mountPoint in cfg.minimum_space_mp else cfg.minimum_space
		requiredSpace = torrentSize - (availableSpace - minimumSpace)
		requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_age, cfg.fallback_ratio
		torrentsDownloading[torrentHash] = mountPoint

		include = override = True
		exclude = False
		freedSpace = 0
		fallbackTorrents = []
		currentDate = datetime.now()

		while freedSpace < requiredSpace:

			if not completedTorrents and not fallbackTorrents:
				break

			if completedTorrents:
				tAge, tLabel, tTracker, tRatio, tSizeBytes, tName, tHash, tPath, parentDirectory = completedTorrents[0]

				if override:
					override = False
					minSize, minAge, minRatio, fbAge, fbRatio = requirements

				if cfg.exclude_unlabelled and not tLabel:
					del completedTorrents[0]
					continue

				if cfg.labels:

					if tLabel in cfg.labels:
						labelRule = cfg.labels[tLabel]
						rule = labelRule[0]

						if rule is exclude:
							del completedTorrents[0]
							continue

						if rule is not include:
							override = True
							minSize, minAge, minRatio, fbAge, fbRatio = labelRule

					elif cfg.labels_only:
						del completedTorrents[0]
						continue

				if cfg.trackers and not override:
					trackerRule = [tracker for tracker in cfg.trackers for url in tTracker if tracker in url[0]]

					if trackerRule:
						trackerRule = cfg.trackers[trackerRule[0]]
						rule = trackerRule[0]

						if rule is exclude:
							del completedTorrents[0]
							continue

						if rule is not include:
							override = True
							minSize, minAge, minRatio, fbAge, fbRatio = trackerRule

						elif cfg.trackers_only:
							del completedTorrents[0]
							continue

				tAge = (currentDate - datetime.utcfromtimestamp(tAge) ).days
				tRatio /= 1000.0
				tSizeGigabytes = tSizeBytes / 1073741824.0

				if tAge < minAge or tRatio < minRatio or tSizeGigabytes < minSize:

						if fbAge is not False and tAge >= fbAge and tSizeGigabytes >= minSize:
							fallbackTorrents.append( (parentDirectory, tHash, tPath, tSizeBytes, tSizeGigabytes) )

						elif fbRatio is not False and tRatio >= fbRatio and tSizeGigabytes >= minSize:
							fallbackTorrents.append( (parentDirectory, tHash, tPath, tSizeBytes, tSizeGigabytes) )

						del completedTorrents[0]
						continue

				del completedTorrents[0]

			else:
				parentDirectory, tHash, tPath, tSizeBytes, tSizeGigabytes = fallbackTorrents.pop(0)

			if mountPoints[parentDirectory] != mountPoint:
				continue

			try:
				self.send('d.open', (tHash,) )
			except:
				continue

			pendingDeletions[mountPoint] += tSizeBytes
			t = Thread(target=self.deleter.process, args=( (tHash, tSizeBytes, tPath, mountPoint),) )
			t.start()
			freedSpace += tSizeGigabytes

		self.cache.lock = False
		self.checkerQueue.release = True

		if freedSpace >= requiredSpace:

			try:
				self.send('d.start', (torrentHash,) )
			except Exception as e:
				logging.error(f"checker.py: XMLRPC Error: Couldn't start torrent: {torrentName}: ")
				return

		if freedSpace < requiredSpace and cfg.enable_email:

			try:
				email(self.cache)
			except Exception as e:
				logging.error(f"checker.py: Email Error: Couldn't send email: {e}")
				return