"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-research
"""
from machine import RTC, Timer
import ntptime as ntp
from ws2812 import WS2812MatrixClock
from wifihandler import WifiHandler
from drivers.button import Button
from config import Config

TIMEZONE = 8
ntp.host = 'ntp.ntsc.ac.cn'


class MatrixClock(WS2812MatrixClock):
	MODE_TIME = 0
	MODE_LIGHT = 1
	MODE_BLINK = 2
	MODE_LIST = ['time', 'light', 'blink']

	__MODE_LAST = MODE_BLINK
	__LIGHT_BRIGHT_MAX = 0.6

	def __init__(self, width=10, height=6, vertical=True):
		super().__init__(width=width, height=height, vertical=vertical)

		self.__rtc = RTC()
		self.__buttons = Button(Config.KEYS.KEY_LIST, click_cb=self.__button_click_cb)
		self.__timer = Timer(0)
		self.__mode = self.MODE_TIME

		self.__power_on = True
		self.__timer_count = 0

		self.clear()
		self.set_brightness(20)

	def sync_time(self, retry=3):
		if WifiHandler.is_sta_connected():
			print('sync time')

			for _ in range(retry):
				try:
					ntp.settime()
					break
				except OSError as ose:
					if str(ose) == '[Errno 116] ETIMEDOUT':
						pass

			print(f'cannot reach ntp host: {ntp.host}, sync time failed')
		else:
			print('no wifi connected, sync time cancelled')

	def show_time(self):
		datetime = self.__rtc.datetime()
		hour = datetime[4] + TIMEZONE
		minute = datetime[5]

		self.set_hour(hour)
		self.set_minute(minute)
		self.show()

	def switch_power(self):
		self.__power_on = not self.__power_on

		self.power_on() if self.__power_on else self.power_off()

	def switch_mode(self):
		self.__mode += 1

		if self.__mode > self.__MODE_LAST:
			self.__mode = 0

	def start(self):
		self.sync_time()
		self.show_time()

		self.__timer.init(
			mode=Timer.PERIODIC,
			period=1000 * 60,
			callback=self.__timer_cb
		)

	def stop(self):
		self.__timer.deinit()
		self.__buttons.deinit()

		self.__timer = None
		self.__buttons = None
		self.__rtc = None


	def __button_click_cb(self, pin):
		# print(f'Key {Config.KEYS.KEY_MAP[pin]} clicked')

		if pin == Config.KEYS.KEY_1:
			self.switch_mode()
		elif pin == Config.KEYS.KEY_2:
			pass
		elif pin == Config.KEYS.KEY_3:
			self.set_brightness(self.brightness - 20)
			self.show_time()
		elif pin == Config.KEYS.KEY_4:
			self.switch_power()

	def __timer_cb(self, _):
		self.show_time()

		self.__timer_count += 1

		if self.__timer_count >= 60:
			self.__timer_count = 0
			self.sync_time()


	@property
	def mode(self):
		return self.__mode

	@mode.setter
	def mode(self, value:int):
		if not isinstance(value, int) or self.MODE_BLINK < value < self.MODE_TIME:
			value = self.MODE_TIME
		
		self.__mode = value
