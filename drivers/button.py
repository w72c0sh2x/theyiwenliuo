"""
Customize Button v1.1

Author: Walkline Wang
Email: walkline@gmail.com
GitHub: walkline80
Gitee: walkline
License: MIT

# IMPORTANT: THIS MODULE ONLY TESTED ON ESP32 BOARD
"""

from machine import Pin, Timer
from utime import ticks_ms


class ButtonException(BaseException):
	pass


class Button(object):
	"""
	- 自定义按钮
	
	支持点击和长按两种模式

	长按模式分为：
	    1. 长按超时触发
	    2. 长按超时松开触发
	
	参数：
	    pin：GPIO 引脚，可使用列表或元组批量添加
	    click_cb：单击事件回调函数
	    press_cb：长按事件回调函数
	    timeout：长按触发超时时间（ms）
		behavior：长按触发模式选择
	"""

	# __BUTTON_RESPONSE_INTERVAL = 20 # 目前使用定时器实现按钮点击并不需要消除抖动
	
	# trigger long press while holding button
	BEHAVIOR_HOLD = 0

	# trigger long press after release button
	BEHAVIOR_RELEASE = 1

	def __init__(self, pin=None, click_cb=None, press_cb=None, timeout=3000, behavior=BEHAVIOR_HOLD, timer_id=10):
		assert pin is not None, ButtonException("pin must be specified")
		assert click_cb is not None or press_cb is not None, ButtonException("at least set one of 'click_cb' or 'press_cb")

		self.button_list = []
		self.__pin_list = []
		self.__button_holding_list = []
		self.__button_status_list = []
		self.__button_pressed_list = []
		self.__last_ticks_list = []

		if isinstance(pin, (list, tuple)):
			for _ in pin:
				self.button_list.append(Pin(_, Pin.IN, Pin.PULL_UP))
				self.__pin_list.append(_)
				self.__button_holding_list.append(False) # true: holding, false: releasing
				self.__button_status_list.append(False) # true: holded, false: released
				self.__button_pressed_list.append(False) # true: pressed once, false: never pressed
				self.__last_ticks_list.append(ticks_ms())
		else:
			self.button_list.append(Pin(pin, Pin.IN, Pin.PULL_UP))
			self.__pin_list.append(pin)
			self.__button_holding_list.append(False)
			self.__button_status_list.append(False)
			self.__button_pressed_list.append(False)
			self.__last_ticks_list.append(ticks_ms())

		self.__click_cb = click_cb # click callback
		self.__press_cb = press_cb # press callback
		self.__timeout = timeout # press callback acting if timed out
		self.__behavior = behavior
		self.__timer = Timer(timer_id)

		self.__timer.init(
			mode=Timer.PERIODIC,
			period=20,
			callback=self.__timer_cb
		)

	def deinit(self):
		for _ in self.button_list:
			_ = None

		self.__timer.deinit()
		self.__timer = None

	def add_button(self, pin):
		self.button_list.append(Pin(pin, Pin.IN, Pin.PULL_UP))
		self.__pin_list.append(pin)
		self.__button_holding_list.append(False)
		self.__button_status_list.append(False)
		self.__button_pressed_list.append(False)
		self.__last_ticks_list.append(ticks_ms())

	def __time_diff(self, index):
		return ticks_ms() - self.__last_ticks_list[index]

	def __timer_cb(self, timer):
		for index in range(len(self.button_list)):
			self.__button_holding_list[index] = not self.button_list[index].value()
			# print("hold" if self.__button_hold else "release")

			if self.__button_holding_list[index]:
				if self.__button_status_list[index] == self.__button_holding_list[index]:
					if self.__time_diff(index) >= self.__timeout and self.__behavior == self.BEHAVIOR_HOLD:
						if self.__press_cb is not None:
							self.__press_cb(self.__time_diff(index), self.__pin_list[index])

						self.__button_status_list[index] = False
						self.__button_pressed_list[index] = True

						self.__last_ticks_list[index] = ticks_ms()
				else:
					if not self.__button_pressed_list[index]:
						self.__button_status_list[index] = True
			else:
				if self.__button_status_list[index]:
					if self.__time_diff(index) >= self.__timeout and self.__behavior == self.BEHAVIOR_RELEASE:
						if self.__press_cb is not None:
							self.__press_cb(self.__time_diff(index), self.__pin_list[index])
					else:
						if self.__click_cb is not None:
							self.__click_cb(self.__pin_list[index])

					self.__button_status_list[index] = False
				else:
					self.__last_ticks_list[index] = ticks_ms()
					self.__button_pressed_list[index] = False

	@property
	def timeout(self):
		return self.__timeout


__press_counts = 0
__led = None

def run_test():
	global __led

	__led = Pin(3, Pin.OUT, value=0)

	from utime import sleep_ms
	import urandom

	def button_click_cb(pin):
		global __led

		__led.value(not __led.value())
		print("button clicked", urandom.randint(0, 65535))
	
	def button_press_cb(duration, pin):
		global __press_counts

		__press_counts += 1
		print("button pressed over {} ms".format(duration))

	button = Button(
		pin=[9, 0],
		click_cb=button_click_cb,
		press_cb=button_press_cb,
		timeout=3000,
		behavior=Button.BEHAVIOR_HOLD
	)

	print(
"""
======================================
       Running button test unit

  Supports:
      1. click
      2. long press (over {} ms)

  Tips:
      Try to click the BOOT button
      Take long press twice to end
======================================
""".format(button.timeout)
	)

	while __press_counts < 2:
		sleep_ms(500)

	button.deinit()
	__led.value(0)

	print(
"""
==========================
    Unit test complete
==========================
"""
	)


if __name__ == "__main__":
	run_test()
