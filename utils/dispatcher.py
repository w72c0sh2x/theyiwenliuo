"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Timer
from utime import sleep
import _thread

try:
	from .utilities import Utilities
except ImportError:
	from utils.utilities import Utilities


class Dispatcher(object):
	'''
	定时器任务调度器
	'''
	__DEFAULT_PERIOD = 20

	def __init__(self, timer_id=0):
		self.__workers = {}
		self.__timer = Timer(timer_id)
		self.__time_counter = 0
		self.__adjusting_rate = 2 if Utilities.is_esp32c3() else 1

		self.__timer.init(
			mode=Timer.PERIODIC,
			period=self.__DEFAULT_PERIOD,
			callback=self.__worker_callback
		)

	def deinit(self):
		self.__timer.deinit()
		self.__workers = {}

	def  __worker_callback(self, _):
		self.__time_counter += 1

		if self.__time_counter > 10 ** 5:
			self.__time_counter = 1

		for worker in self.__workers.values():
			if (self.__time_counter * self.__DEFAULT_PERIOD * self.__adjusting_rate) % worker.period == 0:
				if worker.thread:
					_thread.start_new_thread(worker.do_work, ())
					sleep(0.02)
				else:
					worker.do_work()

	def add_work(self, work, period=100, thread=False):
		'''
		添加一个调度任务
		'''
		if callable(work):
			self.__workers[id(work)] = Worker(work, period, thread)
		else:
			print('work must be a function')

	def del_work(self, work):
		'''
		删除指定的任务
		'''
		if self.__workers.get(work):
			self.__workers.pop(work)

	def del_last_work(self):
		'''
		删除最后一个添加的任务
		'''
		if len(self.__workers) > 0:
			self.__workers.popitem()
	
	def del_works(self):
		'''
		删除所有任务
		'''
		self.__workers.clear()


class Worker(object):
	'''
	定时器任务
	'''
	def __init__(self, work, period, thread=False):
		self.__work = work
		self.__period = period
		self.__thread = thread

	@property
	def period(self):
		return self.__period

	@property
	def thread(self):
		return self.__thread

	def do_work(self):
		self.__work()


if __name__ == '__main__':
	from machine import RTC
	from utime import sleep

	def task1():
		print(f'\t{rtc.datetime()[4:7]} task 1 (3)')
		sleep(0.1)
	
	def task2():
		print(f'{rtc.datetime()[4:7]} task 2 (5)')
		sleep(0.2)

	rtc = RTC()
	rtc.init((2000, 1, 1, 0, 0, 0, 0, 8))

	tasks = Dispatcher()
	tasks.add_work(task1, 3000)
	tasks.add_work(task2, 5000)
