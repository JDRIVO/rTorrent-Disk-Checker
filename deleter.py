import os
import time
import logging
from threading import Thread
from remote_caller import SCGIRequest


class Deleter(SCGIRequest):

	def __init__(self, cache):
		super(Deleter, self).__init__()
		self.cache = cache
		self.removeTorrent = self.cache.removeTorrent
		self.deletions = self.cache.deletions
		self.pending = self.cache.pending
		self.pendingDeletions = self.cache.pendingDeletions
		t = Thread(target=self.processor)
		t.start()

	def processor(self):

		while True:

			while self.deletions:
				self.pending.append(self.deletions[0][:2])
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
			logging.error("deleter.py: XMLRPC Error: Couldn't delete torrent from rtorrent:", e)
			self.pendingDeletions[mountPoint] -= torrentSize

			try:
				self.pending.remove((torrentHash, mountPoint))
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

		t = Thread(target=self.removeTorrent, args=(torrentHash, mountPoint))
		t.start()
