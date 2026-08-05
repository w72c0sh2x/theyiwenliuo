"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Pin
from neopixel import NeoPixel
from utils.utilities import Utilities
Config = Utilities.import_config()


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
