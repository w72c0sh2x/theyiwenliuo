"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from config import Config
from machine import RTC
from utime import sleep, localtime
import ntptime as ntp
from .ws2812 import WS2812MatrixClock
from utils.wifihandler import WifiHandler

TIMEZONE = 8
ntp.host = 'ntp.ntsc.ac.cn'
ntp.NTP_DELTA -= TIMEZONE * 60 * 60
# ntp.host = 'ntp1.aliyun.com'


class MatrixClock(WS2812MatrixClock):
	MODE_TIME = 0
	MODE_LIGHT = 1
	MODE_BLINK = 2
	MODE_LIST = ['time', 'light', 'blink']

	__MODE_LAST = MODE_BLINK
	__LIGHT_BRIGHT_MAX = 0.6

	def __init__(self, width, height, vertical):
		super().__init__(width=width, height=height, vertical=vertical)

		self.__rtc = RTC()
		self.__mode = self.MODE_TIME
		self.__timer_count = 0

		self.clean()
		self.set_brightness(20)

	def sync_time(self, retry=3):
		if WifiHandler.is_sta_connected():
			print('sync time')

			for _ in range(retry):
				try:
					ntp.settime()
					time = localtime()
					print(f'{time[0]}-{time[1]}-{time[2]} {time[3]}:{time[4]}:{time[5]}')
					return
				except OSError as ose:
					if str(ose) == '[Errno 116] ETIMEDOUT':
						pass
				
				sleep(0.5)

			print(f'cannot reach ntp host: {ntp.host}, sync time failed')
		else:
			print('no wifi connected, sync time cancelled')

	def show_time(self):
		datetime = self.__rtc.datetime()
		hour = datetime[4]
		minute = datetime[5]

		self.set_hour(hour)
		self.set_minute(minute)
		
		if self.powered_on:
			self.show()

	def power_on(self):
		self.show_time()

	def power_off(self):
		self.clean()

	def switch_power(self):
		'''
		开启/关闭内容显示
		'''
		self.powered_on = not self.powered_on

		self.power_on() if self.powered_on else self.power_off()

	def switch_mode(self):
		self.__mode += 1

		if self.__mode > self.__MODE_LAST:
			self.__mode = 0

	def start(self):
		self.sync_time()
		self.show_time()

	def stop(self):
		self.__rtc = None

	# 定时器回调函数
	def refresh_time(self):
		self.show_time()

		self.__timer_count += 1

		if self.__timer_count >= Config.PERIOD.CLOCK_SYNC:
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
