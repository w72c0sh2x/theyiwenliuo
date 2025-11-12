"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-research
"""
from config import Config
from utime import sleep
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
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
		clock.set_brightness(clock.brightness - 20)
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

		if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode(timeout_sec=120):
			from matrix.matrix_clock import MatrixClock

			clock = MatrixClock(Config.MATRIX.WIDTH, Config.MATRIX.HEIGHT)
			clock.mode = MatrixClock.MODE_TIME
			clock.start()
			clock.set_bright_max(Config.BRIGHTNESS.MAX)
			clock.auto_brightness()

			tasks = Dispatcher()
			tasks.add_work(clock.refresh_time, Config.PERIOD.CLOCK_MS) #, thread=True)
			tasks.add_work(clock.auto_brightness, Config.PERIOD.ADC_MS) #, thread=True)

			while True:
				sleep(0.5)
		else:
			Utilities.hard_reset()
	except KeyboardInterrupt:
		if tasks: tasks.deinit()
		if clock: clock.stop()
		if buttons: buttons.deinit()
