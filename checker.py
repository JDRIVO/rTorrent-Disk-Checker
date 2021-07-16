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

	def check(self, torrentInfo):
		script, torrentName, torrentHash, torrentPath, torrentSize = torrentInfo
		torrentSize = int(torrentSize) / 1073741824.0

		try:
			reload(cfg)
		except Exception as e:
			self.cache.lock = False
			self.checkerQueue.release = True
			logging.critical("checker.py: {}: Config Error: Couldn't import config file: {}".format(torrentName, e) )
			return

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

		include = override = True
		exclude = no = False
		freedSpace = 0
		fallbackTorrents = []
		currentDate = datetime.now()

		while freedSpace < requiredSpace and (completedTorrentsCopy or fallbackTorrents):

			if completedTorrentsCopy:
				tAge, tLabel, tTracker, tRatio, tSizeBytes, tName, tHash, tPath, parentDirectory = completedTorrentsCopy.pop(0)

				if override:
					override = False
					minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = requirements

				if cfg.exclude_unlabelled and not tLabel:
					continue

				if cfg.labels:

					if tLabel in cfg.labels:
						labelRule = cfg.labels[tLabel]
						rule = labelRule[0]

						if rule is exclude:
							continue

						if rule is not include:

							if "exclude" in labelRule:
								tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

								if tracker:
									continue

							elif "include" in labelRule:
								tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

								if not tracker:
									continue

							override = True
							minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = labelRule[:7]

					elif cfg.labels_only:
						continue

				if cfg.trackers and not override:
					tracker = [tracker for tracker in cfg.trackers for url in tTracker if tracker in url[0]]

					if tracker:
						trackerRule = cfg.trackers[tracker[0]]
						rule = trackerRule[0]

						if rule is exclude:
							continue

						if rule is not include:
							override = True
							minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = trackerRule

					elif cfg.trackers_only:
						continue

				tSizeGigabytes = tSizeBytes / 1073741824.0
				tAgeConverted = (currentDate - datetime.utcfromtimestamp(tAge) ).days
				tRatioConverted = tRatio / 1000.0

				if tSizeGigabytes < minSize or tAgeConverted < minAge or tRatioConverted < minRatio:

					if fbMode == 1:

						if tSizeGigabytes < fbSize or tAgeConverted < fbAge or tRatioConverted < fbRatio:
							continue
						else:
							fallbackTorrents.append(
								(tAge,
								tLabel,
								tTracker,
								tRatio,
								tSizeBytes,
								tSizeGigabytes,
								tName,
								tHash,
								tPath,
								parentDirectory) )

					elif fbMode == 2:

						if (
								fbSize is not no and tSizeGigabytes >= fbSize) or (
								fbAge is not no and tAgeConverted >= fbAge) or (
								fbRatio is not no and tRatioConverted >= fbRatio):
							fallbackTorrents.append(
								(tAge,
								tLabel,
								tTracker,
								tRatio,
								tSizeBytes,
								tSizeGigabytes,
								tName,
								tHash,
								tPath,
								parentDirectory) )

					continue

			else:
				tAge, tLabel, tTracker, tRatio, tSizeBytes, tSizeGigabytes, tName, tHash, tPath, parentDirectory = fallbackTorrents.pop(0)

			if self.mountPoints[parentDirectory] != mountPoint:
				continue

			try:
				completedTorrents.remove([tAge, tLabel, tTracker, tRatio, tSizeBytes, tName, tHash, tPath, parentDirectory])
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
