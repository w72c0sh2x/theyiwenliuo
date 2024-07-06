"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Pin
from neopixel import NeoPixel
from config import Config


class WS2812Matrix(object):
	__BRIGHT_MAX = 0.1
	__BRIGHT_MIN = 0.05

	def __init__(self, width, height, pin=Config.PINS.HSPI_MOSI):
		self.width = width
		self.height = height
		self.__neopixel = NeoPixel(Pin(pin), self.width * self.height)
		self.bright_percent = 0
		self.brightness = 100

	def clear(self):
		self.__neopixel.fill(Config.Colors.BLACK)
		self.show()

	def fill(self, color:tuple(int, tuple)):
		if isinstance(color, int):
			color = int(color * self.bright_percent)
			self.__neopixel.fill((color, color, color))
		elif isinstance(color, tuple) and len(color) == 3:
			self.__neopixel.fill(self.set_color(color))

	def show(self):
		self.__neopixel.write()

	def refresh(self):
		for index in range(self.led_count):
			self.__neopixel[index] = self.set_color(self.__neopixel[index])

		self.show()

	def set_color(self, color:tuple):
		if isinstance(color, tuple) and len(color) == 3:
			r, g, b = color
			r = int(r * self.bright_percent)
			g = int(g * self.bright_percent)
			b = int(b * self.bright_percent)
			color = (r, g, b)

		return color

	@property
	def led_count(self):
		return self.__neopixel.n

	@property
	def led_bpp(self):
		return self.__neopixel.bpp

	@property
	def brightness(self):
		return self.__brightness

	@brightness.setter
	def brightness(self, value:int):
		if not isinstance(value, int) or value <= 10:
			value = 100
		elif value >= 100:
			value = 10

		self.__brightness = value
		value = value / 100

		self.bright_percent = (self.__BRIGHT_MAX - self.__BRIGHT_MIN) * value + self.__BRIGHT_MIN * value
		# self.refresh()


class WS2812MatrixClock(WS2812Matrix):
	HOUR_TENS_PLACE_COLUMN = 0
	HOUR_ONES_PLACE_COLUMN = 4
	MINUTE_TENS_PLACE_COLUMN = 8
	MINUTE_ONES_PLACE_LIST = [] # [5, 11, 17, 23, 29, 35, 41, 47, 53, 59]

	NUM_V0 = 0x7e3f # '111111000111111'
	NUM_V1 = 0x27e1 # '010011111100001'
	NUM_V2 = 0x5ebd # '101111010111101'
	NUM_V3 = 0x56bf # '101011010111111'
	NUM_V4 = 0x709f # '111000010011111'
	NUM_V5 = 0x76b7 # '111011010110111'
	NUM_V6 = 0x7eb7 # '111111010110111'
	NUM_V7 = 0x421f # '100001000011111'
	NUM_V8 = 0x7ebf # '111111010111111'
	NUM_V9 = 0x76bf # '111011010111111'

	NUM_LIST_V = {
		'0': NUM_V0,
		'1': NUM_V1,
		'2': NUM_V2,
		'3': NUM_V3,
		'4': NUM_V4,
		'5': NUM_V5,
		'6': NUM_V6,
		'7': NUM_V7,
		'8': NUM_V8,
		'9': NUM_V9
	}

	def __init__(self, width=10, height=6, vertical=True):
		super().__init__(width, height)

		self.MINUTE_ONES_PLACE_LIST = [self.height - 1 + self.height * count for count in range(width)]
		self.__vertical = vertical
		self.__buf = bytearray(self.led_count * self.led_bpp)

		self.set_brightness(self.brightness)

	def power_on(self):
		self.__neopixel.buf = self.__buf
		self.show()
	
	def power_off(self):
		self.__buf = bytearray(self.__neopixel.buf)
		self.brightness = 0
		self.show()

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
		hour_tens = self.__zfile_bin(self.NUM_LIST_V[hour[0]])
		hour_ones = self.__zfile_bin(self.NUM_LIST_V[hour[1]])

		start = self.HOUR_TENS_PLACE_COLUMN * self.height
		for count in range(3):
			for index, bit in enumerate(hour_tens[count * 5 : count * 5 + 5]):
				self.__neopixel[start + count * self.height + index] = self.__white if bit == '1' else self.__black

		start = self.HOUR_ONES_PLACE_COLUMN * self.height
		for count in range(3):
			for index, bit in enumerate(hour_ones[count * 5:count * 5 + 5]):
				self.__neopixel[start + count * self.height + index] = self.__white if bit == '1' else self.__black

	def set_minute(self, value:int):
		minute = self.__zfill_time(value)
		minute_tens = int(minute[0])
		minute_ones = int(minute[1])

		start = self.MINUTE_TENS_PLACE_COLUMN * self.height

		if minute_tens == 0:
			for index in range(start, start + self.height):
				self.__neopixel[index] = self.__black

		for index in range(minute_tens):
			self.__neopixel[start + index] = self.__blue

		if minute_ones == 0:
			for index in self.MINUTE_ONES_PLACE_LIST:
				self.__neopixel[index] = self.__black

		count = 0
		for index in range(minute_ones):
			count += 1
			green = self.__green

			if 1 <= count <= 3:
				green = self.__green_low
			elif 4 <= count <= 6:
				green = self.__green_medium

			self.__neopixel[self.MINUTE_ONES_PLACE_LIST[index]] = green

	def __zfill_time(self, value:int):
		'''将时分秒填充为 2 位数字符串'''
		value = str(value)
		return '0' + value if len(value) == 1 else value
	
	def __zfile_bin(self, value:int):
		'''将整型转为 15 位二进制字符串'''
		return '{:015b}'.format(value)


if __name__ == '__main__':
	test = WS2812MatrixClock()

	test.set_brightness(20)
	test.set_hour(13)
	test.set_minute(39)
	test.show()
