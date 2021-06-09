from queue import Queue
from threading import Thread

class CheckerQueue:

	def __init__(self):
		self.queue = Queue()
		self.release = True

	def processor(self):

		while True:
			item = self.queue.get()

			if self.release:
				self.startChecker(item)
				self.release = False

			self.queue.task_done()

	def createChecker(self, cache, deleterQueue):
		from checker import Checker
		self.checker = Checker(cache, self, deleterQueue)

	def startChecker(self, item):
		t = Thread(target=self.checker.check, args=(item,) )
		t.start()

	def queueAdd(self, item):
		self.queue.put(item)

class DeleterQueue:

	def __init__(self):
		self.queue = Queue()

	def processor(self):

		while True:
			item = self.queue.get()
			self.startDeleter(item)
			self.queue.task_done()

	def createDeleter(self, cache):
		from deleter import Deleter
		self.deleter = Deleter(cache, self)

	def startDeleter(self, item):
		self.deleter.delete(item)

	def queueAdd(self, item):
		self.queue.put(item)