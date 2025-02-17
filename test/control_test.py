"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from drivers.button import Button
from config import Config


if __name__ == '__main__':
	def buttons_click_cb(pin):
		print(f'Key {Config.KEYS.KEY_MAP[pin]} clicked')

	def buttons_press_cb(time, pin):
		print(f'Key {Config.KEYS.KEY_MAP[pin]} pressed {time} ms')

	buttons = Button(
		Config.KEYS.KEY_LIST,
		click_cb=buttons_click_cb,
		press_cb=buttons_press_cb,
		behavior=Button.BEHAVIOR_HOLD
	)

	print('try to click or hold keys on board')
