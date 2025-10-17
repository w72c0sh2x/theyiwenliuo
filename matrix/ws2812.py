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
		self.__bright_min = self.__BRIGHT_MIN
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

	def set_bright_max(self, value):
		'''
		设置亮度最大值，取值范围 0.0~1.0
		'''
		if 1 < value <= 0:
			self.__bright_max = self.__BRIGHT_MAX
		else:
			self.__bright_max = value
		
	def set_bright_min(self, value):
		if self.__bright_max <= value <= 0:
			self.__bright_min = self.__BRIGHT_MIN
		else:
			self.__bright_min = value

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

		self.__bright_percent = (self.__bright_max - self.__bright_min) * value + self.__bright_min * value
