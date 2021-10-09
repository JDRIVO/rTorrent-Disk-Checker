import time
from queue import Queue
from threading import Thread


class CheckerQueue(Queue):

	def __init__(self, cache, checker):
		super(CheckerQueue, self).__init__()
		self.cache = cache
		self.checker = checker
		t = Thread(target=self.processor)
		t.start()

	def processor(self):

		while True:
			torrent = self.get()

			while self.cache.lock:
				time.sleep(0.000001)

			self.cache.lock = True
			Thread(target=self.checker.check, args=(torrent,)).start()
