"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Pin
from neopixel import NeoPixel
from utils.utilities import Utilities
Config = Utilities.import_config()

GAMMA_LUT22 = (
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2,
	3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6,
	6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11, 11, 12,
	12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19,
	20, 20, 21, 22, 22, 23, 23, 24, 25, 25, 26, 26, 27, 28, 28, 29,
	30, 30, 31, 32, 33, 33, 34, 35, 35, 36, 37, 38, 39, 39, 40, 41,
	42, 43, 43, 44, 45, 46, 47, 48, 49, 49, 50, 51, 52, 53, 54, 55,
	56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
	73, 74, 75, 76, 77, 78, 79, 81, 82, 83, 84, 85, 87, 88, 89, 90,
	91, 93, 94, 95, 97, 98, 99, 100, 102, 103, 105, 106, 107, 109, 110, 111,
	113, 114, 116, 117, 119, 120, 121, 123, 124, 126, 127, 129, 130, 132, 133, 135,
	137, 138, 140, 141, 143, 145, 146, 148, 149, 151, 153, 154, 156, 158, 159, 161,
	163, 165, 166, 168, 170, 172, 173, 175, 177, 179, 181, 182, 184, 186, 188, 190,
	192, 194, 196, 197, 199, 201, 203, 205, 207, 209, 211, 213, 215, 217, 219, 221,
	223, 225, 227, 229, 231, 234, 236, 238, 240, 242, 244, 246, 248, 251, 253, 255,
)

class WS2812Matrix(object):
	__BRIGHT_MAX_VALUE = 200
	__BRIGHT_MIN_VALUE = 1

	def __init__(self, width, height, pin=Config.PINS.DIN):
		self.__width = width
		self.__height = height
		self.__neopixel = NeoPixel(Pin(pin), self.__width * self.__height)
		self.__bright_max = self.__BRIGHT_MAX_VALUE
		self.__bright_percent = 100
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
			color = self.set_color(color)
			self.__neopixel.fill((color, color, color))
		elif isinstance(color, tuple) and len(color) == 3:
			self.__neopixel.fill(self.set_color(color))

	def show(self):
		'''
		显示所有指定的颜色
		'''
		self.__neopixel.write()

	def set_color(self, color:tuple(int, tuple)):
		'''
		设置颜色亮度
		'''
		if isinstance(color, int):
			rel = 255 / self.__bright_max
			color = int((color / rel) * (self.__bright_percent / 100))
			color = GAMMA_LUT22[color]
		if isinstance(color, tuple) and len(color) == 3:
			r, g, b = color
			r = self.set_color(r)
			g = self.set_color(g)
			b = self.set_color(b)
			color = (r, g, b)

		return color

	def set_bright_max(self, value:int):
		'''
		设置亮度最大值，取值范围 1~200
		'''
		if value > self.__BRIGHT_MAX_VALUE or value < self.__BRIGHT_MIN_VALUE:
			self.__bright_max = self.__BRIGHT_MAX_VALUE
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
		return self.__bright_percent

	@brightness.setter
	def brightness(self, value:int):
		'''
		设置亮度百分比
		'''
		self.__bright_percent = 1 if value < 1 else (100 if value > 100 else value)
