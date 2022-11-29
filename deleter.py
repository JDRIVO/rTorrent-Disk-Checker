import os
import time
import logging
from threading import Thread

from remote_caller import SCGIRequest


class Deleter(SCGIRequest):

	def __init__(self, cache):
		super().__init__()
		self.cache = cache
		self.pending = self.cache.pending
		self.deletions = self.cache.deletions

		self.updatePending = self.cache.updatePending
		self.pendingDeletions = self.cache.pendingDeletions
		Thread(target=self.processor).start()

	def processor(self):

		while True:

			while self.deletions:
				self.pending.append(self.deletions[0])
				self.delete(self.deletions.pop(0))

			time.sleep(0.01)

	def delete(self, torrentData):
		torrentHash, mountPoint, torrentSize = torrentData

		try:
			files = self.send("f.multicall", (torrentHash, "", "f.size_bytes=", "f.frozen_path="))
			tHash = (torrentHash,)
			torrentPath = self.send("d.directory", tHash)
			self.send("d.tracker_announce", tHash)
			self.send("d.erase", tHash)
		except Exception as e:
			self.pendingDeletions[mountPoint] -= torrentSize
			logging.error("deleter.py: XMLRPC Error: Couldn't delete torrent from rtorrent: " + str(e))

			try:
				self.pending.remove(torrentData)
			except:
				pass

			return

		if len(files) <= 1:
			self.pendingDeletions[mountPoint] -= files[0][0]

			try:
				os.remove(files[0][1])
			except Exception as e:
				logging.error("deleter.py: File Deletion Error: Skipping file: {}: {}".format(files[0][1], e))

		else:

			for file in files:
				self.pendingDeletions[mountPoint] -= file[0]

				try:
					os.remove(file[1])
				except Exception as e:
					logging.error("deleter.py: File Deletion Error: Skipping file: {}: {}".format(file[1], e))

			try:
				os.rmdir(torrentPath)
			except Exception as e:

				for root, directories, files in os.walk(torrentPath, topdown=False):

					try:
						os.rmdir(root)
					except Exception as e:
						logging.error("deleter.py: Folder Deletion Error: Skipping folder: {}: {}".format(root, e))

		Thread(target=self.updatePending, args=(torrentData,)).start()
