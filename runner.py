"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
__version__ = '0.1'
__version_info__ = (0, 1)
print('module runner version:', __version__)


import gc
from utime import sleep
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
from drivers.button import Button

try:
	MatrixClock = __import__('./matrix/matrix_clock').MatrixClock
except ImportError:
	from matrix.matrix_clock import MatrixClock

gc.collect()

CONFIG = Utilities.import_config()

clock = None
buttons = None
tasks = None

class Runner(object):
	def __init__(self):
		self.__clock = MatrixClock()
		self.__buttons = Button(
			CONFIG.KEYS.KEY_LIST,
			click_cb=self.__buttons_click_cb,
			press_cb=self.__buttons_press_cb,
			timeout=2000,
		)

	def start(self):
		try:
			self.__clock.show_connecting_animation()

			if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode(timeout_sec=120):
				self.__clock.sync_time()
				self.__clock.stop()
				self.__clock.show_blink()
				self.__clock.start()

				gc.collect()

				while True:
					sleep(1)
			else:
				Utilities.hard_reset()
		except KeyboardInterrupt:
			if self.__clock: self.__clock.stop()
			if self.__buttons: self.__buttons.deinit()

	def __buttons_click_cb(self, pin):
		print(f'Key {CONFIG.KEYS.KEY_MAP[pin]} clicked')

		if pin == CONFIG.KEYS.KEY_1:
			if self.__clock.is_menu_mode:
				self.__clock.show_hide_menu(save=False)
			else:
				self.__clock.switch_display_mode()
		elif pin == CONFIG.KEYS.KEY_2:
			if self.__clock.__menu_mode:
				self.__clock.switch_menu()
			else:
				self.__clock.switch_power()

	def __buttons_press_cb(self, time, pin):
		print(f'Key {CONFIG.KEYS.KEY_MAP[pin]} pressed {time} ms')

		if pin == CONFIG.KEYS.KEY_1:
			WifiHandler.delete_sta_config_file()

			if WifiHandler.is_ble_mode():
				WifiHandler.output_wifi_mode_file()
			else:
				WifiHandler.delete_wifi_mode_file()

			Utilities.hard_reset()
		elif pin == CONFIG.KEYS.KEY_2:
			if self.__clock.__last_menu == MatrixClock.MODE_UPDATE:
				self.__clock.check_update()
			else:
				self.__clock.show_hide_menu()


if __name__ == '__main__':
	runner = Runner()
	runner.start()
