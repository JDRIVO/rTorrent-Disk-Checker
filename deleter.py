import os
import logging
from remote_caller import SCGIRequest

class Deleter(SCGIRequest):

	def __init__(self, cache, deleterQueue):
		super().__init__()
		self.cache = cache
		self.deleterQueue = deleterQueue

	def process(self, torrentInfo):
		torrentHash, torrentSize, torrentPath, mountPoint = torrentInfo
		self.cache.pending.append(torrentHash)

		try:
			files = self.send('f.multicall', (torrentHash, '', 'f.size_bytes=', 'f.frozen_path=') )
			tHash = (torrentHash,)
			self.send('d.tracker_announce', tHash)
			self.send('d.erase', tHash)
			self.deleterQueue.queueAdd( (torrentHash, torrentPath, mountPoint, files) )
		except Exception as e:
			logging.error(f"deleter.py: XMLRPC Error: Couldn't delete torrent from rtorrent: {e}")
			self.cache.pendingDeletions[mountPoint] -= torrentSize
			self.cache.pending.remove(torrentHash)

	def delete(self, torrentInfo):
		torrentHash, torrentPath, mountPoint, files = torrentInfo

		if len(files) <= 1:

			try:
				self.cache.pendingDeletions[mountPoint] -= files[0][0]
				os.remove(files[0][1])
			except Exception as e:
				logging.error(f"deleter.py: File Deletion Error: Skipping file: {files[0][1]}: {e}")

		else:

			for file in files:
				self.cache.pendingDeletions[mountPoint] -= file[0]

				try:
					os.remove(file[1])
				except Exception as e:
					logging.error(f"deleter.py: File Deletion Error: Skipping file: {file[1]}: {e}")

			try:
				os.rmdir(torrentPath)
			except Exception as e:
				logging.error(f"deleter.py: Folder Deletion Error: Skipping folder: {torrentPath}: {e}")

				for root, directories, files in os.walk(torrentPath, topdown=False):

					try:
						os.rmdir(root)
					except Exception as e:
						logging.error(f"deleter.py: Folder Deletion Error: Skipping folder: {root}: {e}")

		self.cache.pending.remove(torrentHash)