"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from config import Config
from machine import RTC
from utime import sleep, localtime
import ntptime as ntp
from .ws2812 import WS2812Matrix
from drivers.photoresistor import Photoresistor
from utils.wifihandler import WifiHandler

TIMEZONE = 8
ntp.host = 'ntp.ntsc.ac.cn'
ntp.NTP_DELTA -= TIMEZONE * 60 * 60
# ntp.host = 'ntp1.aliyun.com'


class MatrixClock(WS2812Matrix):
	MODE_TIME = 0
	MODE_LIGHT = 1
	MODE_BLINK = 2
	MODE_LIST = ['time', 'light', 'blink']

	BRIGHTNESS_LEVEL = {
		Photoresistor.LEVEL_1: 95,
		Photoresistor.LEVEL_2: 75,
		Photoresistor.LEVEL_3: 60,
		Photoresistor.LEVEL_4: 45,
		Photoresistor.LEVEL_5: 35,
		Photoresistor.LEVEL_6: 25
	}

	__MODE_LAST = MODE_BLINK
	__LIGHT_BRIGHT_MAX = 0.6

	__HOUR_TENS_PLACE_COLUMN = 0
	__HOUR_ONES_PLACE_COLUMN = 4
	__MINUTE_TENS_PLACE_COLUMN = 8
	__MINUTE_ONES_PLACE_LIST = [] # [5, 11, 17, 23, 29, 35, 41, 47, 53, 59]

	__NUM_V0 = 0x7e3f # '111111000111111'
	__NUM_V1 = 0x27e1 # '010011111100001'
	__NUM_V2 = 0x5ebd # '101111010111101'
	__NUM_V3 = 0x56bf # '101011010111111'
	__NUM_V4 = 0x709f # '111000010011111'
	__NUM_V5 = 0x76b7 # '111011010110111'
	__NUM_V6 = 0x7eb7 # '111111010110111'
	__NUM_V7 = 0x421f # '100001000011111'
	__NUM_V8 = 0x7ebf # '111111010111111'
	__NUM_V9 = 0x76bf # '111011010111111'

	__NUM_LIST_VERTICAL = {
		'0': __NUM_V0,
		'1': __NUM_V1,
		'2': __NUM_V2,
		'3': __NUM_V3,
		'4': __NUM_V4,
		'5': __NUM_V5,
		'6': __NUM_V6,
		'7': __NUM_V7,
		'8': __NUM_V8,
		'9': __NUM_V9
	}

	def __init__(self, width, height):
		super().__init__(width, height)

		self.__MINUTE_ONES_PLACE_LIST = [self.__height - 1 + self.__height * count for count in range(width)]

		self.__rtc = RTC()
		self.__adc = Photoresistor(Config.PINS.ADC)
		self.__mode = self.MODE_TIME
		self.__timer_count = 0
		self.__last_adc_level = 0

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

				sleep(0.2)

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
		self.__adc = None

	# 定时器回调函数
	def refresh_time(self):
		self.__timer_count += 1

		if self.__timer_count >= Config.PERIOD.CLOCK_SYNC:
			print('sync time per 1 hour')
			self.__timer_count = 0
			self.sync_time()

		self.show_time()

	# 定时器回调函数
	def auto_brightness(self):
		adc_level = self.__adc.level

		if self.__last_adc_level != adc_level:
			self.__last_adc_level = adc_level
		else:
			return

		self.set_brightness(self.BRIGHTNESS_LEVEL[adc_level])
		self.show_time()
		print(f'set brightness level to {adc_level}')

	def set_brightness(self, value):
		self.brightness = value
		self.__black = Config.Colors.BLACK
		self.__white = self.set_color(Config.Colors.WHITE)
		self.__blue = self.set_color(Config.Colors.BLUE)
		self.__green = self.set_color(Config.Colors.GREEN)
		self.__green_medium = self.set_color(Config.Colors.GREEN_MEDIUM)
		self.__green_low = self.set_color(Config.Colors.GREEN_LOW)

	def set_hour(self, value:int):
		hour = self.__zfill_time(value)
		hour_tens = self.__zfile_bin(self.__NUM_LIST_VERTICAL[hour[0]])
		hour_ones = self.__zfile_bin(self.__NUM_LIST_VERTICAL[hour[1]])

		start = self.__HOUR_TENS_PLACE_COLUMN * self.__height
		for count in range(3):
			for index, bit in enumerate(hour_tens[count * 5 : count * 5 + 5]):
				self.__neopixel[start + count * self.__height + index] = self.__white if bit == '1' else self.__black

		start = self.__HOUR_ONES_PLACE_COLUMN * self.__height
		for count in range(3):
			for index, bit in enumerate(hour_ones[count * 5:count * 5 + 5]):
				self.__neopixel[start + count * self.__height + index] = self.__white if bit == '1' else self.__black

	def set_minute(self, value:int):
		minute = self.__zfill_time(value)
		minute_tens = int(minute[0])
		minute_ones = int(minute[1])

		start = self.__MINUTE_TENS_PLACE_COLUMN * self.__height

		# if minute_tens == 0:
		for index in range(start, start + self.__height):
			self.__neopixel[index] = self.__black

		for index in range(minute_tens):
			self.__neopixel[start + index] = self.__blue

		# if minute_ones == 0:
		for index in self.__MINUTE_ONES_PLACE_LIST:
			self.__neopixel[index] = self.__black

		count = 0
		for index in range(minute_ones):
			count += 1
			green = self.__green

			if 1 <= count <= 3:
				green = self.__green_low
			elif 4 <= count <= 6:
				green = self.__green_medium

			self.__neopixel[self.__MINUTE_ONES_PLACE_LIST[index]] = green

	def __zfill_time(self, value:int):
		'''将时分秒填充为 2 位数字符串'''
		value = str(value)
		return '0' + value if len(value) == 1 else value
	
	def __zfile_bin(self, value:int):
		'''将整型转为 15 位二进制字符串'''
		return '{:015b}'.format(value)

	@property
	def mode(self):
		return self.__mode

	@mode.setter
	def mode(self, value:int):
		if not isinstance(value, int) or self.MODE_BLINK < value < self.MODE_TIME:
			value = self.MODE_TIME
		
		self.__mode = value


if __name__ == '__main__':
	test = MatrixClock(9, 6)

	test.set_brightness(20)
	test.set_hour(13)
	test.set_minute(39)
	test.show()
