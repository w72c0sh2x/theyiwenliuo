"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-research
"""
from config import Config
from utime import sleep
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
from matrix.matrix_clock import MatrixClock
from drivers.button import Button
from utils.dispatcher import Dispatcher
import sys

sys.path.insert(0, '/')

clock = None
buttons = None
tasks = None


def buttons_click_cb(pin):
	print(f'Key {Config.KEYS.KEY_MAP[pin]} clicked')
	if not clock: return

	if pin == Config.KEYS.KEY_1:
		clock.switch_mode()
	elif pin == Config.KEYS.KEY_2:
		pass
	elif pin == Config.KEYS.KEY_3:
		bright = clock.brightness - 20

		clock.set_brightness(100 if bright < 1 else bright)
		clock.show_time()
	elif pin == Config.KEYS.KEY_4:
		clock.switch_power()

def buttons_press_cb(time, pin):
	print(f'Key {Config.KEYS.KEY_MAP[pin]} pressed {time} ms')

	if pin == Config.KEYS.KEY_1:
		Utilities.delete_sta_config_file()
		Utilities.hard_reset()


if __name__ == '__main__':
	try:
		buttons = Button(
			Config.KEYS.KEY_LIST,
			click_cb=buttons_click_cb,
			press_cb=buttons_press_cb
		)

		tasks = Dispatcher()
		clock = MatrixClock(Config.MATRIX.WIDTH, Config.MATRIX.HEIGHT)
		clock.set_bright_max(Config.BRIGHTNESS.MAX)
		tasks.add_work(clock.show_connecting, 50)

		if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode(timeout_sec=120):
			clock.mode = MatrixClock.MODE_TIME
			clock.start()
			tasks.del_works()
			clock.clean()
			clock.auto_brightness()

			tasks.add_work(clock.refresh_time, Config.PERIOD.CLOCK_MS)
			tasks.add_work(clock.auto_brightness, Config.PERIOD.ADC_MS)

			while True:
				sleep(1)
		else:
			Utilities.hard_reset()
	except KeyboardInterrupt:
		if tasks: tasks.deinit()
		if clock: clock.stop()
		if buttons: buttons.deinit()
