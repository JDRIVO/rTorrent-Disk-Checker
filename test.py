import os
import sys
import utils

try:
	import config as cfg
except Exception as e:
	print("Error: Couldn't import config file:", e)
	sys.exit(1)

from datetime import datetime
from collections import deque
from remote_caller import SCGIRequest

try:
	torrentPath = sys.argv[2]
except Exception:
	torrentPath = "/"

rtxmlrpc = SCGIRequest()

completedTorrents = rtxmlrpc.send(
	"d.multicall2",
	(
		"",
		"complete",
		"d.name=",
		"d.directory=",
		"d.hash=",
		"d.custom1=",
		"t.multicall=,t.url=",
		"d.timestamp.finished=",
		"d.ratio=",
		"t.multicall=,t.url=,t.scrape_complete=",
		"d.size_bytes=",
	),
)

mountPoints = {}

for torrentData in completedTorrents:
	tName, tPath = torrentData[:2]
	parentDirectory = tPath.rsplit("/", 1)[0] if tName in tPath else tPath
	mountPoint = [path for path in [parentDirectory.rsplit('/', n)[0] for n in range(parentDirectory.count('/'))] if os.path.ismount(path)]
	mountPoint = mountPoint[0] if mountPoint else "/"
	mountPoints[parentDirectory] = mountPoint

mountPoint = [path for path in [torrentPath.rsplit('/', n)[0] for n in range(torrentPath.count('/'))] if os.path.ismount(path)]
mountPoint = mountPoint[0] if mountPoint else "/"

completedTorrents = [
	(
		tName,
		tHash,
		tLabel,
		tTracker,
		(datetime.now() - datetime.utcfromtimestamp(tAge)).days,
		tRatio / 1000.0,
		max([seeds[1] for seeds in tSeeds]),
		tSize,
		tSize / 1073741824.0,
	)
	for tName, tPath, tHash, tLabel, tTracker, tAge, tRatio, tSeeds, tSize in completedTorrents
	if mountPoints[tPath.rsplit("/", 1)[0] if tName in tPath else tPath] == mountPoint
]
completedTorrents = utils.sortTorrents(cfg.sort_order, cfg.group_order, completedTorrents)

whitelist, blacklist = "whitelist", "blacklist"
include, exclude = "include", "exclude"
labelRules, trackerRules = {}, {}
override = True

requirements = (
	cfg.general_rules["age"] if "age" in cfg.general_rules else False,
	cfg.general_rules["ratio"] if "ratio" in cfg.general_rules else False,
	cfg.general_rules["seeds"] if "seeds" in cfg.general_rules else False,
	cfg.general_rules["size"] if "size" in cfg.general_rules else False,
	cfg.general_rules["fb_mode"] if "fb_mode" in cfg.general_rules else False,
	cfg.general_rules["fb_age"] if "fb_age" in cfg.general_rules else False,
	cfg.general_rules["fb_ratio"] if "fb_ratio" in cfg.general_rules else False,
	cfg.general_rules["fb_seeds"] if "fb_seeds" in cfg.general_rules else False,
	cfg.general_rules["fb_size"] if "fb_size" in cfg.general_rules else False,
)
utils.convertRules(cfg.label_rules, labelRules)
utils.convertRules(cfg.tracker_rules, trackerRules)

start = datetime.now()
torrentSize = float(sys.argv[1])
completedTorrentsCopy = deque(completedTorrents)
torrentsDownloading, pendingDeletions = {}, {}
lastModified = os.path.getmtime("config.py")

if lastModified > 0: pass

if not cfg.enable_cache: pass

try:
	mountPoint = mountPoints[torrentPath]
except Exception:
	mountPoint = [path for path in [torrentPath.rsplit('/', n)[0] for n in range(torrentPath.count('/'))] if os.path.ismount(path)]
	mountPoint = mountPoint[0] if mountPoint else "/"
	mountPoints[torrentPath] = mountPoint

try:
	downloads = torrentsDownloading[mountPoint]

	if downloads:

		try:
			downloading = self.send("d.multicall2", ("", "leeching", "d.left_bytes=", "d.hash=", "d.state="))
			downloading = sum([tBytes for tBytes, tHash, tState in downloading if tHash in downloads and tState])
		except Exception as e:
			print(e)

	else:
		downloading = 0

	downloads.append(None)

except Exception:
	torrentsDownloading[mountPoint] = [None]
	downloading = 0

try:
	deletions = pendingDeletions[mountPoint]
except Exception:
	deletions = pendingDeletions[mountPoint] = 0

disk = os.statvfs(mountPoint)
availableSpace = (disk.f_bsize * disk.f_bavail + deletions - downloading) / 1073741824.0
minimumSpace = cfg.minimum_space_mp[mountPoint] if mountPoint in cfg.minimum_space_mp else cfg.minimum_space
requiredSpace = torrentSize - (availableSpace - minimumSpace)

freedSpace = count = 0
labelMatch = False
trackers = {}
deletedTorrents = []
fallbackTorrents = deque()

while freedSpace < requiredSpace and (completedTorrentsCopy or fallbackTorrents):

	if completedTorrentsCopy:
		torrent = completedTorrentsCopy.popleft()
		tName, tHash, tLabel, tTracker, tAge, tRatio, tSeeds, tSizeBytes, tSizeGigabytes = torrent

		if cfg.exclude_unlabelled and not tLabel:
			continue

		if override:
			override = False
			minAge, minRatio, minSeeds, minSize, fbMode, fbAge, fbRatio, fbSeeds, fbSize = requirements

		if labelRules:

			if tLabel in labelRules:
				labelRule = labelRules[tLabel]

				if labelRule is exclude:
					continue

				if labelRule is not include:

					if blacklist in labelRule:

						try:
							tracker = trackers[tLabel + tTracker[0][0]]
						except Exception:
							tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

							for url in tTracker:
								trackers[tLabel + url[0]] = tracker

						if tracker:
							continue

					elif whitelist in labelRule:

						try:
							tracker = trackers[tLabel + tTracker[0][0]]
						except Exception:
							tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

							for url in tTracker:
								trackers[tLabel + url[0]] = tracker

						if not tracker:
							continue

					if include not in labelRule:
						override = True
						minAge, minRatio, minSeeds, minSize, fbMode, fbAge, fbRatio, fbSeeds, fbSize = labelRule[:9]

				labelMatch = True

			elif cfg.labels_only:
				continue
			else:
				labelMatch = False

		if trackerRules and not override:

			try:
				tracker = trackers[tTracker[0][0]]
			except Exception:
				tracker = [tracker for tracker in trackerRules for url in tTracker if tracker in url[0]]

				for url in tTracker:
					trackers[url[0]] = tracker

			if tracker:
				trackerRule = trackerRules[tracker[0]]

				if trackerRule is exclude:
					continue

				if trackerRule is not include:
					override = True
					minAge, minRatio, minSeeds, minSize, fbMode, fbAge, fbRatio, fbSeeds, fbSize = trackerRule[:9]

			elif cfg.trackers_only or (cfg.labels_and_trackers_only and not labelMatch):
				continue

		if tAge < minAge or tRatio < minRatio or tSeeds < minSeeds or tSizeGigabytes < minSize:

			if fbMode == 1:

				if tAge >= fbAge and tRatio >= fbRatio and tSeeds >= fbSeeds and tSizeGigabytes >= fbSize:
					fallbackTorrents.append(torrent)

			elif fbMode == 2:

				if (
					(fbAge is not False and tAge >= fbAge)
					or (fbRatio is not False and tRatio >= fbRatio)
					or (fbSeeds is not False and tSeeds >= fbSeeds)
					or (fbSize is not False and tSizeGigabytes >= fbSize)
				):
					fallbackTorrents.append(torrent)

			continue

	else:
		torrent = fallbackTorrents.popleft()
		tName, tHash, tLabel, tTracker, tAge, tRatio, tSeeds, tSizeBytes, tSizeGigabytes = torrent

	try:
		completedTorrents.remove(torrent)
	except Exception:
		continue

	count += 1
	deletedTorrents.append((count, torrent))
	pendingDeletions[mountPoint] += tSizeBytes
	freedSpace += tSizeGigabytes

finish = datetime.now() - start
availableSpaceAfter = availableSpace + freedSpace - torrentSize
availableSpaceAfter = 0 if availableSpaceAfter < 0 else availableSpaceAfter

info1 = "TA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TR = Torrent Ratio  TS = Torrent Size  TSS = Torrent Seeds  TT = Torrent Tracker"
info2 = "Script Executed in {} Seconds\n{} Torrent(s) Deleted Totaling {:.2f} GB".format(finish, count, freedSpace)
info3 = "{:.2f} GB Free Space Before Torrent Download\n{:.2f} GB Free Space After {:.2f} GB Torrent Download".format(
	availableSpace, availableSpaceAfter, torrentSize
)

with open("testresult.txt", "w+") as textFile:
	textFile.write(info2 + "\n")
	textFile.write(info3 + "\n\n")
	textFile.write(info1 + "\n\n")

	for count, torrentData in deletedTorrents:
		(
			tName,
			tHash,
			tLabel,
			tTracker,
			tAge,
			tRatio,
			tSeeds,
			tSizeBytes,
			tSizeGigabytes,
		) = torrentData
		info = "{}. TA: {} Days Old\n{}. TN: {}\n{}. TL: {}\n{}. TR: {}\n{}. TS: {:.2f} GB\n{}. TSS: {}\n{}. TT: {}\n".format(
			count,
			tAge,
			count,
			tName,
			count,
			tLabel,
			count,
			tRatio,
			count,
			tSizeGigabytes,
			count,
			tSeeds,
			count,
			", ".join(tracker[0] for tracker in tTracker),
		)
		textFile.write(info + "\n")
		print(info)

print("{}\n\n{}\n{}\n".format(info1, info2, info3))
print("Your result has been saved to testresult.txt\n")
