"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Pin, Timer
from random import randint
from neopixel import NeoPixel
from config import Config
from drivers.button import Button


def color_generator(random=False):
	count = 0
	step = 5

	while True:
		if random:
			yield randint(0, 65)
		else:
			yield count

			count += step

			if count >= 125 or count <= 0:
				step = -step

def button_click_cb(pin):
	global test_index
	test_index = 0 if test_index == test_max else test_index + 1

	if test_index == 5:
		clean()

def button_press_cb(time, pin):
	global test_index
	test_index = 0
	clean()

def timer_test_cb(_):
	global test_index, test_5_index

	if test_index == 1:
		neopixel.fill((next(colors), 0, 0))
		neopixel.write()
	elif test_index == 2:
		neopixel.fill((0, next(colors), 0))
		neopixel.write()
	elif test_index == 3:
		neopixel.fill((0, 0, next(colors)))
		neopixel.write()
	elif test_index == 4:
		color = next(colors)
		neopixel.fill((color, color, color))
		neopixel.write()
	elif test_index == 5:
		neopixel[test_5_index] = (next(colors_random), next(colors_random), next(colors_random))
		neopixel.write()

		test_5_index += 1

		if test_5_index >= neopixel.n:
			clean()
			test_5_index = 0
	elif test_index == 6:
		for _ in range(neopixel.n):
			neopixel[_] = (next(colors_random), next(colors_random), next(colors_random))

		neopixel.write()

def clean():
	neopixel.fill((0, 0, 0))
	neopixel.write()


neopixel = NeoPixel(Pin(Config.PINS.DIN), Config.MATRIX.WIDTH * Config.MATRIX.HEIGHT)

test_index = 0
test_max = 6
test_5_index = 0

colors = color_generator()
colors_random = color_generator(True)


if __name__ == '__main__':
	button_test = Button(
		Config.KEYS.KEY_TEST,
		click_cb=button_click_cb,
		press_cb=button_press_cb,
		timeout=2000
	)

	timer_test = Timer(8)
	timer_test.init(
		mode=Timer.PERIODIC,
		period=20,
		callback=timer_test_cb
	)

	clean()
	print('click test key to switch test items, hold key to stop')
