"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Pin
from neopixel import NeoPixel

try:
	from utils.utilities import Utilities
except ImportError:
	Utilities = __import__('utils/utilities').Utilities


CONFIG = Utilities.import_config()


class WS2812(object):
	def __init__(self, width, height, pin):
		self.__width = width
		self.__height = height
		self.__neopixel = NeoPixel(Pin(pin), self.__width * self.__height)

		# 设备当前亮度值（百分比）
		# brightness = __bright_percent * bright_max
		self.__bright_percent = 100

	def clean(self):
		'''清除屏幕（黑屏）'''
		self.__neopixel.fill(CONFIG.COLORS.BLACK)
		self.__neopixel.write()

	def fill(self, color:tuple):
		'''填充指定颜色，参数支持 tuple(r, g, b)'''
		if isinstance(color, tuple) and len(color) == 3:
			self.__neopixel.fill(self.convert_color(color))
			self.__neopixel.write()

	def show(self):
		'''显示所有指定的颜色'''
		self.__neopixel.write()

	def convert_color(self, color:tuple):
		'''设置颜色亮度'''
		if isinstance(color, tuple) and len(color) == 3:
			h, s, v = self.__rgb_to_hsv(*color)
			v *= CONFIG.BRIGHTNESS.MAX / 100 * self.__bright_percent / 100
			color = self.__hsv_to_rgb(h, s, v)

		return color

	def __rgb_to_hsv(self, r:int, g:int, b:int) -> tuple:
		r, g, b = r / 255.0, g / 255.0, b / 255.0
		max_value = max(r, g, b)
		min_value = min(r, g, b)
		delta = max_value - min_value
		if delta == 0:
			return 0, 0, max_value
		elif max_value == r:
			h = (g - b) / delta % 6
		elif max_value == g:
			h = (b - r) / delta + 2
		elif max_value == b:
			h = (r - g) / delta + 4
		h = h * 60
		if h < 0:
			h += 360
		s = delta / max_value
		v = max_value
		return h, s, v

	def __hsv_to_rgb(self, h:float, s:float, v:float) -> tuple:
		if s == 0:
			r, g, b = v, v, v
		else:
			h = h / 60.0
			i = int(h)
			f = h - i
			p = v * (1 - s)
			q = v * (1 - s * f)
			t = v * (1 - s * (1 - f))
			if i == 0:
				r, g, b = v, t, p
			elif i == 1:
				r, g, b = q, v, p
			elif i == 2:
				r, g, b = p, v, t
			elif i == 3:
				r, g, b = p, q, v
			elif i == 4:
				r, g, b = t, p, v
			else:
				r, g, b = v, p, q

		return int(r * 255), int(g * 255), int(b * 255)

	@property
	def led_count(self):
		return self.__neopixel.n

	@property
	def led_bpp(self):
		return self.__neopixel.bpp

	@property
	def brightness(self) -> int:
		return self.__bright_percent

	@brightness.setter
	def brightness(self, value:int):
		'''获取/设置亮度百分比'''
		self.__bright_percent = 1 if value < 1 else (100 if value > 100 else value)


if __name__ == '__main__':
	from utime import sleep_ms
	from random import choice

	SKYBLUE = (9, 171, 255)
	LIGHTGREEN = (121, 234, 0)
	BLUE = (2, 79, 195)
	GREEN_MEDIUM = (55, 231, 253)
	DARKGRAY = (54, 54, 54)
	COLORS = (SKYBLUE, LIGHTGREEN, BLUE, GREEN_MEDIUM, DARKGRAY)

	ws2812 = WS2812(9, 6, CONFIG.PINS.DIN_MATRIX)

	for _ in range(10):
		color = choice(COLORS)
		for percent in range(1, 101):
			ws2812.brightness = percent
			ws2812.fill(color)
			sleep_ms(20)

		color = choice(COLORS)
		for percent in range(100, 0, -1):
			ws2812.brightness = percent
			ws2812.fill(color)
			sleep_ms(20)
