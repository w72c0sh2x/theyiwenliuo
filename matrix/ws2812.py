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

	def __init__(self, width, height, pin=Config.PINS.DIN):
		self.__width = width
		self.__height = height
		self.__neopixel = NeoPixel(Pin(pin), self.__width * self.__height)
		self.__bright_percent = 0
		self.__bright_max = self.__BRIGHT_MAX
		self.__brightness = 100
		self.powered_on = True

	def clean(self):
		'''
		清除屏幕（黑屏）
		'''
		self.__neopixel.fill(Config.Colors.BLACK)
		self.show()

	def fill(self, color:tuple(int, tuple)):
		'''
		填充指定颜色，参数支持 int 和 tuple (r, g, b)
		'''
		if isinstance(color, int):
			color = int(color * self.__bright_percent)
			self.__neopixel.fill((color, color, color))
		elif isinstance(color, tuple) and len(color) == 3:
			self.__neopixel.fill(self.set_color(color))

	def show(self):
		'''
		显示所有指定的颜色
		'''
		self.__neopixel.write()

	def refresh(self):
		'''
		刷新显示内容
		'''
		for index in range(self.led_count):
			self.__neopixel[index] = self.set_color(self.__neopixel[index])

		self.show()

	def set_color(self, color:tuple):
		'''
		设置颜色亮度
		'''
		if isinstance(color, tuple) and len(color) == 3:
			r, g, b = color
			r = int(r * self.__bright_percent)
			g = int(g * self.__bright_percent)
			b = int(b * self.__bright_percent)
			color = (r, g, b)

		return color

	def set_bright_max(self, value=0.0):
		'''
		设置亮度最大值，取值范围 0.0~1.0
		'''
		if 1 < value <= 0:
			self.__bright_max = self.__BRIGHT_MAX
		else:
			self.__bright_max = value

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
		if not self.powered_on:
			return

		if not isinstance(value, int) or value <= 10:
			value = 100
		elif value >= 100:
			value = 10

		self.__brightness = value
		value = value / 100

		self.__bright_percent = (self.__bright_max - self.__BRIGHT_MIN) * value + self.__BRIGHT_MIN * value
		# self.refresh()


class WS2812MatrixClock(WS2812Matrix):
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

	def __init__(self, width, height, vertical):
		super().__init__(width, height)

		self.__MINUTE_ONES_PLACE_LIST = [self.__height - 1 + self.__height * count for count in range(width)]
		self.__vertical = vertical

		self.set_brightness(self.brightness)

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


if __name__ == '__main__':
	test = WS2812MatrixClock(9, 6, True)

	test.set_brightness(20)
	test.set_hour(13)
	test.set_minute(39)
	test.show()
