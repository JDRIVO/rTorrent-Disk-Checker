import os
import time
import importlib
from remote_caller import SCGIRequest
import config as cfg

class Cache(SCGIRequest):

	def __init__(self):
		super().__init__()
		self.pendingDeletions = {}
		self.lastNotification = None
		self.torrentsDownloading = {}
		self.torrents = None
		self.lock = False
		self.pending = []

	def getTorrents(self):

		while True:

			while self.lock or self.pending:
				time.sleep(60)

			try:
				torrents = self.send('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.name=', 'd.hash=', 'd.directory=') )
			except:
				time.sleep(60)
				continue

			torrents.sort()
			[item.append(item[7].rsplit('/', 1)[0]) if item[5] in item[7] else item.append(item[7]) for item in torrents]
			self.torrents = torrents

			if self.torrentsDownloading:
				downloading = [tHash[0] for tHash in self.send('d.multicall2', ('', 'leeching', 'd.hash=') )]

				for torrentHash in list(self.torrentsDownloading):

					if torrentHash not in downloading:
						del self.torrentsDownloading[torrentHash]

			importlib.reload(cfg)
			time.sleep(cfg.cache_interval)

	def getMountPoints(self):
		self.mountPoints = {}

		while not self.torrents:
			time.sleep(1)

		for item in self.torrents:
			parentDirectory = item[8]
			mountPoint = [path for path in [parentDirectory.rsplit('/', num)[0] for num in range(parentDirectory.count('/') )] if os.path.ismount(path)]
			mountPoint = mountPoint[0] if mountPoint else '/'
			self.mountPoints[parentDirectory] = mountPoint