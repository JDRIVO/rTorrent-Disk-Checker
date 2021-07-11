import time
from queue import Queue
from threading import Thread
from checker import Checker


class CheckerQueue(Queue):

	def __init__(self):
		super(CheckerQueue, self).__init__()
		self.release = True
		t = Thread(target=self.processor)
		t.start()

	def processor(self):

		while True:

			if self.release:
				item = self.get()
				self.cache.lock = True
				self.startChecker(item)
				self.release = False

			time.sleep(0.000001)

	def createChecker(self, cache):
		self.cache = cache
		self.checker = Checker(cache, self)

	def startChecker(self, item):
		t = Thread(target=self.checker.check, args=(item,) )
		t.start()
