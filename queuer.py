import time
from queue import Queue
from threading import Thread
from checker import Checker
from deleter import Deleter


class CheckerQueue(Queue):

	def __init__(self):
		super(CheckerQueue, self).__init__()
		self.release = True

	def processor(self):

		while True:

			if self.release:
				item = self.get()
				self.cache.lock = True
				self.startChecker(item)
				self.release = False

			time.sleep(0.000001)

	def createChecker(self, cache, deleterQueue):
		self.cache = cache
		self.checker = Checker(cache, self, deleterQueue)

	def startChecker(self, item):
		t = Thread(target=self.checker.check, args=(item,) )
		t.start()


class DeleterQueue(Queue):

	def __init__(self):
		super(DeleterQueue, self).__init__()

	def processor(self):

		while True:
			item = self.get()
			self.startDeleter(item)

	def createDeleter(self, cache):
		self.deleter = Deleter(cache, self)

	def startDeleter(self, item):
		self.deleter.delete(item)
