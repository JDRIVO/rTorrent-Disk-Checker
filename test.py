import os
import sys
from datetime import datetime
from remote_caller import SCGIRequest

rtxmlrpc = SCGIRequest()

completedTorrents = rtxmlrpc.send(
	'd.multicall2',
	('',
	'complete',
	'd.timestamp.finished=',
	'd.custom1=',
	't.multicall=,t.url=',
	'd.ratio=',
	'd.size_bytes=',
	'd.name=',
	'd.hash=',
	'd.directory=') )
completedTorrents.sort()
[item.append(item[7].rsplit('/', 1)[0]) if item[5] in item[7] else item.append(item[7]) for item in completedTorrents]

mountPoints = {}

for item in completedTorrents:
	parentDirectory = item[8]
	mountPoint = [path for path in [parentDirectory.rsplit('/', n)[0] for n in range(parentDirectory.count('/') )] if os.path.ismount(path)]
	mountPoint = mountPoint[0] if mountPoint else '/'
	mountPoints[parentDirectory] = mountPoint

torrentPath = sys.argv[2]

if torrentPath == '0':
	torrentPath = '/'

start = datetime.now()
torrentSize = float(sys.argv[1])

try:
	import config as cfg
except Exception as e:
	print(e)

completedTorrentsCopy = completedTorrents[:]
torrentsDownloading, pendingDeletions = {}, {}

if torrentPath in mountPoints:
	mountPoint = mountPoints[torrentPath]
else:
	mountPoint = [path for path in [torrentPath.rsplit('/', n)[0] for n in range(torrentPath.count('/') )] if os.path.ismount(path)]
	mountPoint = mountPoint[0] if mountPoint else '/'
	mountPoints[torrentPath] = mountPoint

try:
	downloads = torrentsDownloading[mountPoint]

	if downloads:

		try:
			downloading = rtxmlrpc.send('d.multicall2', ('', 'leeching', 'd.left_bytes=', 'd.hash=') )
			downloading = sum(tBytes for tBytes, tHash in downloading if tHash in downloads)
		except Exception as e:
			print(e)

	else:
		downloading = 0

	downloads.append(None)

except:
	torrentsDownloading[mountPoint] = [None]
	downloading = 0

if mountPoint in pendingDeletions:
	deletions = pendingDeletions[mountPoint]
else:
	deletions = pendingDeletions[mountPoint] = 0

disk = os.statvfs(mountPoint)
availableSpace = (disk.f_bsize * disk.f_bavail + deletions - downloading) / 1073741824.0
minimumSpace = cfg.minimum_space_mp[mountPoint] if mountPoint in cfg.minimum_space_mp else cfg.minimum_space
requiredSpace = torrentSize - (availableSpace - minimumSpace)
requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_mode, cfg.fallback_size, cfg.fallback_age, cfg.fallback_ratio

include = override = True
exclude = no = False
freedSpace = count = 0
trackers = {}
fallbackTorrents, deletedTorrents = [], []
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

						try:
							tracker = trackers[tLabel + tTracker[0][0]]
						except:
							tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

							for url in tTracker:
								trackers[tLabel + url[0]] = tracker

						if tracker:
							continue

					elif "include" in labelRule:

						try:
							tracker = trackers[tLabel + tTracker[0][0]]
						except:
							tracker = [tracker for tracker in labelRule[-1] for url in tTracker if tracker in url[0]]

							for url in tTracker:
								trackers[tLabel + url[0]] = tracker

						if not tracker:
							continue

					override = True
					minSize, minAge, minRatio, fbMode, fbSize, fbAge, fbRatio = labelRule[:7]

			elif cfg.labels_only:
				continue

		if cfg.trackers and not override:

			try:
				tracker = trackers[tTracker[0][0]]
			except:
				tracker = [tracker for tracker in cfg.trackers for url in tTracker if tracker in url[0]]

				for url in tTracker:
					trackers[url[0]] = tracker

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
						tAgeConverted,
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
						tAgeConverted,
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
		tAge, tAgeConverted, tLabel, tTracker, tRatio, tSizeBytes, tSizeGigabytes, tName, tHash, tPath, parentDirectory = fallbackTorrents.pop(0)

	if mountPoints[parentDirectory] != mountPoint:
		continue

	try:
		completedTorrents.remove([tAge, tLabel, tTracker, tRatio, tSizeBytes, tName, tHash, tPath, parentDirectory])
	except:
		continue

	count += 1
	deletedTorrents.append('%s. TA: %s Days Old\n%s. TN: %s\n%s. TL: %s\n%s. TT: %s\n' % (count, tAgeConverted, count, tName, count, tLabel, count, tTracker) )
	pendingDeletions[mountPoint] += tSizeBytes
	freedSpace += tSizeGigabytes

finish = datetime.now() - start
availableSpaceAfter = availableSpace + freedSpace - torrentSize

with open('testresult.txt', 'w+') as textFile:
	textFile.write('Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB\n' % (finish, count, freedSpace) )
	textFile.write('%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download\n\n' % (availableSpace, availableSpaceAfter, torrentSize) )
	textFile.write('TA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n\n')

	for torrent in deletedTorrents:
		print(torrent)
		textFile.write(torrent + '\n')

print('TA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n')
print('Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB' % (finish, count, freedSpace) )
print('%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download\n' % (availableSpace, availableSpaceAfter, torrentSize) )
