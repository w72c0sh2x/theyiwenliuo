"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Pin, ADC
from random import randint
from neopixel import NeoPixel
from drivers.button import Button
from utils.utilities import Utilities

try:
	from dispatcher import Dispatcher
except ImportError:
	from utils.dispatcher import Dispatcher

CONFIG = Utilities.import_config()


class HardwareTest(object):
	def __init__(self):
		self.__neopixel = NeoPixel(Pin(CONFIG.PINS.DIN_MATRIX), CONFIG.WS2812_MATRIX.WIDTH * CONFIG.WS2812_MATRIX.HEIGHT)

		self.__buttons = Button(
			CONFIG.KEYS.KEY_LIST,
			click_cb=self.__buttons_click_cb,
			press_cb=self.__buttons_press_cb,
			timeout=1000,
			behavior=Button.BEHAVIOR_HOLD,
			timer_id=None
		)

		self.__adc = ADC(Pin(CONFIG.PINS.BRIGHTNESS_ADC))
		self.__adc.atten(ADC.ATTN_11DB)

		self.__colors = self.__color_generator()
		self.__task = lambda: self.__buttons_press_task()

		self.__tasks = Dispatcher()
		self.__tasks.add_work(self.__buttons.timer_callback, 20)

		self.clean()

	def __color_generator(self):
		while True:
			yield randint(0, 100)

	def __buttons_click_cb(self, pin):
		self.__tasks.del_work(self.__task)

		print(f'Key {CONFIG.KEYS.KEY_MAP[pin]} clicked, adc value: {self.__adc.read()}')

		self.__neopixel.fill((next(self.__colors), next(self.__colors), next(self.__colors)))
		self.__neopixel.write()

	def __buttons_press_cb(self, time, pin):
		print(f'Key {CONFIG.KEYS.KEY_MAP[pin]} pressed {time} ms')

		self.__tasks.add_work(self.__task, 100)

	def __buttons_press_task(self):
		for _ in range(self.__neopixel.n):
			self.__neopixel[_] = (next(self.__colors), next(self.__colors), next(self.__colors))

		self.__neopixel.write()

	def clean(self):
		self.__neopixel.fill((0, 0, 0))
		self.__neopixel.write()


if __name__ == '__main__':
	print('Test running...\r\n- Click or press keys on board\r\n- Press Ctrl+D to terminate')

	test = HardwareTest()
