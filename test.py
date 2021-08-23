import os
import sys
from datetime import datetime
from collections import deque
from remote_caller import SCGIRequest

try:
	import config as cfg
except Exception as e:
	print(e)

rtxmlrpc = SCGIRequest()

completedTorrents = rtxmlrpc.send(
	'd.multicall2',
	('',
	'complete',
	'd.timestamp.finished=',
	'd.ratio=',
	'd.name=',
	'd.custom1=',
	't.multicall=,t.url=',
	'd.hash=',
	'd.directory=',
	'd.size_bytes=') )

completedTorrents.sort()
completedTorrents = [tData[2:] + [tData[-1] / 1073741824.0, tData[1] / 1000.0, datetime.utcfromtimestamp(tData[0]),
		tData[6].rsplit('/', 1)[0] if tData[2] in tData[6] else tData[6]] for tData in completedTorrents]

mountPoints = {}

for torrentData in completedTorrents:
	parentDirectory = torrentData[-1]
	mountPoint = [path for path in [parentDirectory.rsplit('/', n)[0] for n in range(parentDirectory.count('/') )] if os.path.ismount(path)]
	mountPoint = mountPoint[0] if mountPoint else '/'
	mountPoints[parentDirectory] = mountPoint

torrentPath = sys.argv[2]

if torrentPath == '0':
	torrentPath = '/'

whitelist = 'whitelist'
blacklist = 'blacklist'
exclude = no = False
include = override = True
labelRules, trackerRules = {}, {}

def addRules(mode, dic):

	if include in mode:

		for title in mode[include]:
			dic[title] = include

	if exclude in mode:

		for title in mode[exclude]:
			dic[title] = exclude

	for title, rules in mode.items():

		if title not in (include, exclude):
			dic[title] = rules

addRules(cfg.labels, labelRules)
addRules(cfg.trackers, trackerRules)

start = datetime.now()
torrentSize = float(sys.argv[1])
completedTorrentsCopy = deque(completedTorrents)
torrentsDownloading, pendingDeletions = {}, {}
lastModified = os.path.getmtime('config.py')

if lastModified > 0: pass

try:
	mountPoint = mountPoints[torrentPath]
except:
	mountPoint = [path for path in [torrentPath.rsplit('/', n)[0] for n in range(torrentPath.count('/') )] if os.path.ismount(path)]
	mountPoint = mountPoint[0] if mountPoint else '/'
	mountPoints[torrentPath] = mountPoint

try:
	downloads = torrentsDownloading[mountPoint]

	if downloads:

		try:
			downloading = self.send('d.multicall2', ('', 'leeching', 'd.left_bytes=', 'd.hash=', 'd.state=') )
			downloading = sum(tBytes for tBytes, tHash, tState in downloading if tHash in downloads and tState)
		except Exception as e:
			print(e)

	else:
		downloading = 0

	downloads.append(None)

except:
	torrentsDownloading[mountPoint] = [None]
	downloading = 0

try:
	deletions = pendingDeletions[mountPoint]
except:
	deletions = pendingDeletions[mountPoint] = 0

disk = os.statvfs(mountPoint)
availableSpace = (disk.f_bsize * disk.f_bavail + deletions - downloading) / 1073741824.0
minimumSpace = cfg.minimum_space_mp[mountPoint] if mountPoint in cfg.minimum_space_mp else cfg.minimum_space
requiredSpace = torrentSize - (availableSpace - minimumSpace)
requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_mode, cfg.fallback_size, cfg.fallback_age, cfg.fallback_ratio

freedSpace = count = 0
trackers = {}
deletedTorrents = []
fallbackTorrents = deque()
currentTime = datetime.now()

while freedSpace < requiredSpace and (completedTorrentsCopy or fallbackTorrents):

	if completedTorrentsCopy:
		torrent = completedTorrentsCopy.popleft()
		tName, tLabel, tTracker, tHash, tPath, tSizeBytes, tSizeGigabytes, tRatio, tAge, parentDirectory = torrent

		if override:
			override = False
			minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = requirements

		if cfg.exclude_unlabelled and not tLabel:
			continue

		if labelRules:

			if tLabel in labelRules:
				labelRule = labelRules[tLabel]

				if labelRule is exclude:
					continue

				if labelRule is not include:

					if blacklist in labelRule:

						try:
							tracker = trackers[tLabel + tTracker[0][0]]
						except:
							tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

							for url in tTracker:
								trackers[tLabel + url[0]] = tracker

						if tracker:
							continue

					elif whitelist in labelRule:

						try:
							tracker = trackers[tLabel + tTracker[0][0]]
						except:
							tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

							for url in tTracker:
								trackers[tLabel + url[0]] = tracker

						if not tracker:
							continue

					if labelRule[0] is not include:
						override = True
						minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = labelRule[:7]

			elif cfg.labels_only:
				continue

		if trackerRules and not override:

			try:
				tracker = trackers[tTracker[0][0]]
			except:
				tracker = [tracker for tracker in trackerRules for url in tTracker if tracker in url[0]]

				for url in tTracker:
					trackers[url[0]] = tracker

			if tracker:
				trackerRule = trackerRules[tracker[0]]

				if trackerRule is exclude:
					continue

				if trackerRule is not include:
					override = True
					minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = trackerRule

			elif cfg.trackers_only:
				continue

		tAgeDays = (currentTime - tAge).days

		if tSizeGigabytes < minSize or tRatio < minRatio or tAgeDays < minAge:

			if fbMode == 1:

				if tSizeGigabytes >= fbSize and tRatio >= fbRatio and tAgeDays >= fbAge:
					fallbackTorrents.append( (torrent, tAgeDays) )

			elif fbMode == 2:

				if (
						fbSize is not no and tSizeGigabytes >= fbSize) or (
						fbRatio is not no and tRatio >= fbRatio) or (
						fbAge is not no and tAgeDays >= fbAge):
					fallbackTorrents.append( (torrent, tAgeDays) )

			continue

	else:
		torrentInfo = fallbackTorrents.popleft()
		torrent = torrentInfo[0]
		tAgeDays = torrentInfo[1]
		tName, tLabel, tTracker, tHash, tPath, tSizeBytes, tSizeGigabytes, tRatio, tAge, parentDirectory = torrent

	if mountPoints[parentDirectory] != mountPoint:
		continue

	try:
		completedTorrents.remove(torrent)
	except:
		continue

	count += 1
	deletedTorrents.append( (count, tAgeDays, tName, tLabel, tTracker, tRatio, tSizeGigabytes) )
	pendingDeletions[mountPoint] += tSizeBytes
	freedSpace += tSizeGigabytes

finish = datetime.now() - start
availableSpaceAfter = availableSpace + freedSpace - torrentSize
availableSpaceAfter = 0 if availableSpaceAfter < 0 else availableSpaceAfter

info1 = 'TA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TR = Torrent Ratio  TS = Torrent Size  TT = Torrent Tracker'
info2 = 'Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB' % (finish, count, freedSpace)
info3 = '%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download' % (availableSpace, availableSpaceAfter, torrentSize)

with open('testresult.txt', 'w+') as textFile:
	textFile.write(info2)
	textFile.write(info3)
	textFile.write('\n\n' + info1 + '\n\n')

	for count, tAgeDays, tName, tLabel, tTracker, tRatio, tSize in deletedTorrents:
		txt = '%s. TA: %s Days Old\n%s. TN: %s\n%s. TL: %s\n%s. TR: %s\n%s. TS: %.2f GB\n%s. TT: %s\n' % \
		(count, tAgeDays, count, tName, count, tLabel, count, tRatio, count, tSize, count, ', '.join(tracker[0] for tracker in tTracker) )
		textFile.write(txt + '\n')
		print(txt)

print(info1 + '\n\n' + info2, info3 + '\n')
