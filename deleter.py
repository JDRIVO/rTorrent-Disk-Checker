import os
from remote_caller import SCGIRequest

class Deleter(SCGIRequest):

	def __init__(self, cache, deleterQueue):
		super().__init__()
		self.cache = cache
		self.deleterQueue = deleterQueue

	def process(self, torrentInfo):
		torrentHash, torrentPath, mountPoint = torrentInfo
		self.cache.pending.append(torrentHash)
		files = self.send('f.multicall', (torrentHash, '', 'f.size_bytes=', 'f.frozen_path=') )
		tHash = (torrentHash,)
		self.send('d.tracker_announce', tHash)
		self.send('d.erase', tHash)
		self.deleterQueue.queueAdd( (torrentHash, torrentPath, mountPoint, files) )

	def delete(self, torrentInfo):
		torrentHash, torrentPath, mountPoint, files = torrentInfo

		if len(files) <= 1:

			try:
				self.cache.pendingDeletions[mountPoint] -= files[0][0]
				os.remove(files[0][1])
			except:
				pass

		else:

			for file in files:
				self.cache.pendingDeletions[mountPoint] -= file[0]
				os.remove(file[1])

			try:
				os.rmdir(torrentPath)
			except:

				for root, directories, files in os.walk(torrentPath, topdown=False):

					try:
						os.rmdir(root)
					except:
						pass

		self.cache.pending.remove(torrentHash)