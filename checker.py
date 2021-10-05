import os
import logging
import config as cfg
from collections import deque
from remote_caller import SCGIRequest
from utils import convertRules
from messenger import message
from deleter import Deleter

try:
	from importlib import reload
except:
	from imp import reload

include = "include"
exclude = "exclude"
whitelist = "whitelist"
blacklist = "blacklist"


class Checker(SCGIRequest):

	def __init__(self, cache):
		super(Checker, self).__init__()
		self.cache = cache
		deleter = Deleter(self.cache)
		self.delete = deleter.deletions
		self.mountPoints = self.cache.mountPoints

		self.torrentsDownloading = self.cache.torrentsDownloading
		self.pendingDeletions = self.cache.pendingDeletions
		self.cfgGeneralRules = self.cfgLabelRules = self.cfgTrackerRules = self.lastHash = None
		self.lastModified = 0

	def check(self, torrentData):
		torrentName, torrentHash, torrentPath, torrentSize = torrentData[1:]
		parentDirectory = torrentPath.rsplit("/", 1)[0] if torrentName in torrentPath else torrentPath
		torrentSize = int(torrentSize) / 1073741824.0
		lastModified = os.path.getmtime("config.py")

		try:
			mountPoint = self.mountPoints[parentDirectory]
		except:
			mountPoint = [path for path in [parentDirectory.rsplit("/", n)[0] for n in range(parentDirectory.count("/"))] if os.path.ismount(path)]
			mountPoint = mountPoint[0] if mountPoint else "/"
			self.mountPoints[parentDirectory] = mountPoint

		if lastModified > self.lastModified:

			try:
				reload(cfg)
			except Exception as e:
				self.cache.lock = False
				logging.critical("checker.py: {}: Config Error: Couldn't import config file: {}".format(torrentName, e))
				return

			if self.cfgLabelRules != cfg.label_rules:
				self.cfgLabelRules = cfg.label_rules
				self.labelRules, self.trackers = {}, {}
				convertRules(cfg.label_rules, self.labelRules)

			if self.cfgTrackerRules != cfg.tracker_rules:
				self.cfgTrackerRules = cfg.tracker_rules
				self.trackerRules, self.trackers = {}, {}
				convertRules(cfg.tracker_rules, self.trackerRules)

			if self.cfgGeneralRules != cfg.general_rules:
				self.cfgGeneralRules = cfg.general_rules
				self.requirements = (
					cfg.general_rules["age"] if "age" in cfg.general_rules else False,
					cfg.general_rules["ratio"] if "ratio" in cfg.general_rules else False,
					cfg.general_rules["seeders"] if "seeders" in cfg.general_rules else False,
					cfg.general_rules["size"] if "size" in cfg.general_rules else False,
					cfg.general_rules["fb_mode"] if "fb_mode" in cfg.general_rules else False,
					cfg.general_rules["fb_age"] if "fb_age" in cfg.general_rules else False,
					cfg.general_rules["fb_ratio"] if "fb_ratio" in cfg.general_rules else False,
					cfg.general_rules["fb_seeders"] if "fb_seeders" in cfg.general_rules else False,
					cfg.general_rules["fb_size"] if "fb_size" in cfg.general_rules else False,
				)

			self.lastModified = lastModified

		if not cfg.enable_cache and self.cache.refreshTorrents():
			self.cache.lock = False
			logging.critical("checker.py: {}: XMLRPC Error: Couldn't retrieve torrents".format(torrentName))
			return

		try:
			completedTorrents = self.cache.torrents[mountPoint]
			completedTorrentsCopy = deque(completedTorrents)
		except:
			completedTorrentsCopy = None

		try:
			downloading = self.torrentsDownloading[mountPoint]

			if downloading:

				try:
					torrentsDownloading = self.send("d.multicall2", ("", "leeching", "d.left_bytes=", "d.hash=", "d.state="))
					torrentsDownloading = sum([tBytes for tBytes, tHash, tState in torrentsDownloading if tHash in downloading and tState])
				except Exception as e:
					self.cache.lock = False
					logging.critical("checker.py: {}: XMLRPC Error: Couldn't retrieve torrents: {}".format(torrentName, e))
					return

			else:
				torrentsDownloading = 0

			downloading.append(torrentHash)

		except:
			self.torrentsDownloading[mountPoint] = [torrentHash]
			torrentsDownloading = 0

		try:
			pendingDeletions = self.pendingDeletions[mountPoint]
		except:
			pendingDeletions = self.pendingDeletions[mountPoint] = 0

		disk = os.statvfs(mountPoint)
		availableSpace = (disk.f_bsize * disk.f_bavail + pendingDeletions - torrentsDownloading) / 1073741824.0
		minimumSpace = cfg.minimum_space_mp[mountPoint] if mountPoint in cfg.minimum_space_mp else cfg.minimum_space
		requiredSpace = torrentSize - (availableSpace - minimumSpace)

		freedSpace = 0
		override = True
		labelMatch = False
		fallbackTorrents = deque()

		while freedSpace < requiredSpace and (completedTorrentsCopy or fallbackTorrents):

			if completedTorrentsCopy:
				torrent = completedTorrentsCopy.popleft()
				tHash, tAge, tLabel, tTracker, tSeeders, tRatio, tSizeBytes, tSizeGigabytes = torrent

				if cfg.exclude_unlabelled and not tLabel:
					continue

				if override:
					override = False
					minAge, minRatio, minSeeders, minSize, fbMode, fbAge, fbRatio, fbSeeders, fbSize = self.requirements

				if self.labelRules:

					if tLabel in self.labelRules:
						labelRule = self.labelRules[tLabel]

						if labelRule is exclude:
							continue

						if labelRule is not include:

							if blacklist in labelRule:

								try:
									tracker = self.trackers[tLabel + tTracker[0][0]]
								except:
									tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

									for url in tTracker:
										self.trackers[tLabel + url[0]] = tracker

								if tracker:
									continue

							elif whitelist in labelRule:

								try:
									tracker = self.trackers[tLabel + tTracker[0][0]]
								except:
									tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

									for url in tTracker:
										self.trackers[tLabel + url[0]] = tracker

								if not tracker:
									continue

							if include not in labelRule:
								override = True
								minAge, minRatio, minSeeders, minSize, fbMode, fbAge, fbRatio, fbSeeders, fbSize = labelRule[:9]

						labelMatch = True

					elif cfg.labels_only:
						continue
					else:
						labelMatch = False

				if self.trackerRules and not override:

					try:
						tracker = self.trackers[tTracker[0][0]]
					except:
						tracker = [tracker for tracker in self.trackerRules for url in tTracker if tracker in url[0]]

						for url in tTracker:
							self.trackers[url[0]] = tracker

					if tracker:
						trackerRule = self.trackerRules[tracker[0]]

						if trackerRule is exclude:
							continue

						if trackerRule is not include:
							override = True
							minAge, minRatio, minSeeders, minSize, fbMode, fbAge, fbRatio, fbSeeders, fbSize = trackerRule[:9]

					elif cfg.trackers_only or (cfg.labels_and_trackers_only and not labelMatch):
						continue

				if tAge < minAge or tRatio < minRatio or tSeeders < minSeeders or tSizeGigabytes < minSize:

					if fbMode == 1:

						if tAge >= fbAge and tRatio >= fbRatio and tSeeders >= fbSeeders and tSizeGigabytes >= fbSize:
							fallbackTorrents.append(torrent)

					elif fbMode == 2:

						if (
							(fbAge is not False and tAge >= fbAge)
							or (fbRatio is not False and tRatio >= fbRatio)
							or (fbSeeders is not False and tSeeders >= fbSeeders)
							or (fbSize is not False and tSizeGigabytes >= fbSize)
						):
							fallbackTorrents.append(torrent)

					continue

			else:
				torrent = fallbackTorrents.popleft()
				tHash, tAge, tLabel, tTracker, tSeeders, tRatio, tSizeBytes, tSizeGigabytes = torrent

			try:
				completedTorrents.remove(torrent)
			except:
				continue

			self.delete.append((tHash, mountPoint, tSizeBytes))
			self.pendingDeletions[mountPoint] += tSizeBytes
			freedSpace += tSizeGigabytes

		if freedSpace >= requiredSpace:
			self.cache.lock = False

			try:
				self.send("d.start", (torrentHash,))
			except Exception as e:
				logging.error("checker.py: {}: XMLRPC Error: Couldn't start torrent: {}".format(torrentName, e))

		else:

			if cfg.repeat_check and self.lastHash != torrentHash:
				self.lastHash = torrentHash
				self.torrentsDownloading[mountPoint].remove(torrentHash)
				self.cache.refreshTorrents()
				self.check(torrentData)

			self.cache.lock = False

			if cfg.enable_email or cfg.enable_pushbullet or cfg.enable_telegram or cfg.enable_slack:

				try:
					message()
				except Exception as e:
					logging.error("checker.py: Message Error: Couldn't send message: " + str(e))
