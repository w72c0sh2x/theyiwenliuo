"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-research
"""
from config import Config
from machine import reset
from utils.wifihandler import WifiHandler
from drivers.button import Button

clock = None
buttons = None


if __name__ == '__main__':
	try:
		if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode():
			from matrix.matrix_clock import MatrixClock

			def button_click_cb(pin):
				# print(f'Key {Config.KEYS.KEY_MAP[pin]} clicked')

				if pin == Config.KEYS.KEY_1:
					clock.switch_mode()
				elif pin == Config.KEYS.KEY_2:
					pass
				elif pin == Config.KEYS.KEY_3:
					clock.set_brightness(clock.brightness - 20)
					clock.show_time()
				elif pin == Config.KEYS.KEY_4:
					clock.switch_power()

			buttons = Button(
				Config.KEYS.KEY_LIST,
				click_cb=button_click_cb
			)

			clock = MatrixClock(Config.MATRIX.WIDTH, Config.MATRIX.HEIGHT, Config.MATRIX.VERTICAL)
			clock.mode = MatrixClock.MODE_TIME
			clock.start()
		else:
			reset()
	except KeyboardInterrupt:
		if clock: clock.stop()
		if buttons: buttons.deinit()
