"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Pin
from utime import sleep
from neopixel import NeoPixel
from config import Config
from drivers.button import Button


__neopixel = NeoPixel(Pin(7), 9 * 6)
# __neopixel.fill((8, 8, 8))
# __neopixel.write()

for _ in range(30):
	__neopixel.fill((32, 32, 32))
	__neopixel.write()
	sleep(0.05)
	__neopixel.fill((0, 0, 0))
	__neopixel.write()
	sleep(0.05)

# for r in range(10, 64):
# 	for g in range(10, 64):
# 		for b in range(10, 64, 5):
# 			__neopixel.fill((r, g, b))
# 			__neopixel.write()
