"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Timer
import _thread


class Dispatcher(object):
	'''
	定时器任务调度器
	'''
	__DEFAULT_PERIOD = 100

	def __init__(self, timer_id=0):
		self.__workers = {}
		self.__timer = Timer(timer_id)
		self.__time_counter = 0

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
			if (self.__time_counter * self.__DEFAULT_PERIOD) % worker.period == 0:
				_thread.start_new_thread(worker.do_work, ())
				sleep(0.02)

	def add_work(self, work, period=100):
		'''
		添加一个调度任务
		'''
		if callable(work):
			self.__workers[id(work)] = Worker(period, work)
		else:
			print('work must be a function')


class Worker(object):
	'''
	定时器任务
	'''
	def __init__(self, period, work):
		self.__period = period
		self.__work = work

	@property
	def period(self):
		return self.__period

	def do_work(self):
		self.__work()


if __name__ == '__main__':
	from machine import RTC
	from utime import sleep

	def task1():
		print(f'\t{rtc.datetime()[4:7]} task 1 (3)')
		sleep(0.8)
	
	def task2():
		print(f'{rtc.datetime()[4:7]} task 2 (5)')
		sleep(0.5)

	rtc = RTC()
	rtc.init((2000, 1, 1, 0, 0, 0, 0, 8))

	tasks = Dispatcher()
	tasks.add_work(task1, 3000)
	tasks.add_work(task2, 5000)
