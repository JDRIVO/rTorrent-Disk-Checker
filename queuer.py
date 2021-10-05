import time
from queue import Queue
from threading import Thread
from checker import Checker


class CheckerQueue(Queue):

	def __init__(self, cache):
		super(CheckerQueue, self).__init__()
		self.cache = cache
		self.checker = Checker(self.cache, self)
		t = Thread(target=self.processor)
		t.start()

	def processor(self):

		while True:
			torrent = self.get()

			while self.cache.lock:
				time.sleep(0.000001)

			self.cache.lock = True
			t = Thread(target=self.checker.check, args=(torrent,))
			t.start()
