import sys
import os
from datetime import datetime
from emailer import email
from remote_caller import SCGIRequest

rtxmlrpc = SCGIRequest()

completedTorrents = rtxmlrpc.send('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.name=', 'd.hash=', 'd.directory=') )
completedTorrents.sort()
[item.append(item[7].rsplit('/', 1)[0]) if item[5] in item[7] else item.append(item[7]) for item in completedTorrents]

mountPoints = {}

for item in completedTorrents:
	parentDirectory = item[8]
	mountPoint = [path for path in [parentDirectory.rsplit('/', num)[0] for num in range(parentDirectory.count('/') )] if os.path.ismount(path)]
	mountPoint = mountPoint[0] if mountPoint else '/'
	mountPoints[parentDirectory] = mountPoint

torrentPath = sys.argv[2]

if torrentPath == '0':
	torrentPath = '/'

start = datetime.now()
torrentSize = int(sys.argv[1])

try:
	import config as cfg
except Exception as e:
	print(e)

completedTorrentsCopy = completedTorrents[:]
torrentsDownloading = []
pendingDeletions = {}

if torrentPath in mountPoints:
	mountPoint = mountPoints[torrentPath]
else:
	mountPoint = [path for path in [torrentPath.rsplit('/', num)[0] for num in range(torrentPath.count('/') )] if os.path.ismount(path)]
	mountPoint = mountPoint[0] if mountPoint else '/'
	mountPoints[torrentPath] = mountPoint

if torrentsDownloading:

	try:
		downloading = rtxmlrpc.send('d.multicall2', ('', 'leeching', 'd.left_bytes=', 'd.hash=') )
		downloading = sum(tBytes for tBytes, tHash in downloading if tHash != torrentHash and torrentsDownloading[tHash] == mountPoint)
	except Exception as e:
		print(e)

else:
	downloading = 0

if mountPoint in pendingDeletions:
	deletions = pendingDeletions[mountPoint]
else:
	deletions = pendingDeletions[mountPoint] = 0

disk = os.statvfs(mountPoint)
availableSpace = (disk.f_bsize * disk.f_bavail + deletions - downloading) / 1073741824.0
minimumSpace = cfg.minimum_space_mp[mountPoint] if mountPoint in cfg.minimum_space_mp else cfg.minimum_space
requiredSpace = torrentSize - (availableSpace - minimumSpace)
requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_age, cfg.fallback_ratio

include = override = True
exclude = False
freedSpace = count = 0
fallbackTorrents, deletedTorrents = [], []
currentDate = datetime.now()

while freedSpace < requiredSpace:

	if not completedTorrentsCopy and not fallbackTorrents:
		break

	if completedTorrentsCopy:
		tAge, tLabel, tTracker, tRatio, tSizeBytes, tName, tHash, tPath, parentDirectory = completedTorrentsCopy[0]

		if override:
			override = False
			minSize, minAge, minRatio, fbAge, fbRatio = requirements

		if cfg.exclude_unlabelled and not tLabel:
			del completedTorrentsCopy[0]
			continue

		if cfg.labels:

			if tLabel in cfg.labels:
				labelRule = cfg.labels[tLabel]
				rule = labelRule[0]

				if rule is exclude:
					del completedTorrentsCopy[0]
					continue

				if rule is not include:
					override = True
					minSize, minAge, minRatio, fbAge, fbRatio = labelRule

			elif cfg.labels_only:
				del completedTorrentsCopy[0]
				continue

		if cfg.trackers and not override:
			trackerRule = [tracker for tracker in cfg.trackers for url in tTracker if tracker in url[0]]

			if trackerRule:
				trackerRule = cfg.trackers[trackerRule[0]]
				rule = trackerRule[0]

				if rule is exclude:
					del completedTorrentsCopy[0]
					continue

				if rule is not include:
					override = True
					minSize, minAge, minRatio, fbAge, fbRatio = trackerRule

				elif cfg.trackers_only:
					del completedTorrentsCopy[0]
					continue

		tAgeConverted = (currentDate - datetime.utcfromtimestamp(tAge) ).days
		tRatioConverted = tRatio / 1000.0
		tSizeGigabytes = tSizeBytes / 1073741824.0

		if tAgeConverted < minAge or tRatioConverted < minRatio or tSizeGigabytes < minSize:

			if fbAge is not False and tAgeConverted >= fbAge and tSizeGigabytes >= minSize:
				fallbackTorrents.append( (tAge, tLabel, tTracker, tRatio, tSizeBytes, tSizeGigabytes, tName, tHash, tPath, parentDirectory) )
			elif fbRatio is not False and tRatioConverted >= fbRatio and tSizeGigabytes >= minSize:
				fallbackTorrents.append( (tAge, tLabel, tTracker, tRatio, tSizeBytes, tSizeGigabytes, tName, tHash, tPath, parentDirectory) )

			del completedTorrentsCopy[0]
			continue

		del completedTorrentsCopy[0]

	else:
		tAge, tLabel, tTracker, tRatio, tSizeBytes, tSizeGigabytes, tName, tHash, tPath, parentDirectory = fallbackTorrents.pop(0)

	if mountPoints[parentDirectory] != mountPoint:
		continue

	try:
		rtxmlrpc.send('d.open', (tHash,) )
	except:
		continue

	pendingDeletions[mountPoint] += tSizeBytes
	completedTorrents.remove([tAge, tLabel, tTracker, tRatio, tSizeBytes, tName, tHash, tPath, parentDirectory])
	deletedTorrents.append('%s. TA: %s Days Old\n%s. TN: %s\n%s. TL: %s\n%s. TT: %s\n' % (count, tAgeConverted, count, tName, count, tLabel, count, tTracker) )
	count += 1
	freedSpace += tSizeGigabytes

finish = datetime.now() - start
availableSpaceAfter = availableSpace + freedSpace - torrentSize

with open('testresult.txt', 'w+') as textfile:
	textfile.write('Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB\n' % (finish, count, freedSpace) )
	textfile.write('%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download\n\n' % (availableSpace, availableSpaceAfter, torrentSize) )
	textfile.write('TA = Torrent Age  TN = Torrent Name	 TL = Torrent Label	 TT = Torrent Tracker\n\n')

	for torrent in deletedTorrents:
		print(torrent)
		textfile.write(torrent + '\n')

print('TA = Torrent Age	 TN = Torrent Name	TL = Torrent Label	TT = Torrent Tracker\n')
print('Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB' % (finish, count, freedSpace) )
print('%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download\n' % (availableSpace, availableSpaceAfter, torrentSize) )