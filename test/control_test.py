"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from drivers.button import Button
from config import Config

def buttons_click_cb(pin):
	print(f'Key {Config.KEYS.KEY_MAP[pin]} clicked')

buttons = Button(Config.KEYS.KEY_LIST, click_cb=buttons_click_cb)
