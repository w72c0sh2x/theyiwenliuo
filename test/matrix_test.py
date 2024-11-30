"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from machine import Pin
from neopixel import NeoPixel
from config import Config
from drivers.button import Button


__neopixel = NeoPixel(Pin(14), 9 * 6)
__neopixel.fill((128, 128, 128))
__neopixel.write()
