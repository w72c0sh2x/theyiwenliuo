"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-research
"""
from config import Config
from machine import Timer
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
from drivers.button import Button
from drivers.photoresistor import Photoresistor
from utils.dispatcher import Dispatcher

clock = None
buttons = None
adc = None
adc_timer = None
last_adc_level = 0

BRIGHTNESS_LEVEL = {
	Photoresistor.LEVEL_1: 95,
	Photoresistor.LEVEL_2: 75,
	Photoresistor.LEVEL_3: 60,
	Photoresistor.LEVEL_4: 35,
	Photoresistor.LEVEL_5: 20
}


def init_buttons():
	global clock, buttons

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

	buttons = Button(
		Config.KEYS.KEY_LIST,
		click_cb=buttons_click_cb,
		press_cb=buttons_press_cb
	)

# 定时器回调函数
def auto_brightness():
	global clock, adc, last_adc_level

	adc_level = adc.level

	if last_adc_level != adc_level:
		last_adc_level = adc_level
		print(f'adc level: {adc_level}')
	else:
		return

	clock.set_brightness(BRIGHTNESS_LEVEL[adc_level])
	clock.show_time()


if __name__ == '__main__':
	try:
		init_buttons()

		if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode():
			from matrix.matrix_clock import MatrixClock

			clock = MatrixClock(Config.MATRIX.WIDTH, Config.MATRIX.HEIGHT, Config.MATRIX.VERTICAL)
			clock.mode = MatrixClock.MODE_TIME
			clock.start()

			adc = Photoresistor(Config.PINS.ADC)

			tasks = Dispatcher()
			tasks.add_work(auto_brightness, 1000 * 3)
			tasks.add_work(clock.refresh_time, 1000 * 10)

			# adc_timer = Timer(8)
			# adc_timer.init(
			# 	mode=Timer.PERIODIC,
			# 	period=1000 * 3,
			# 	callback=adc_timer_cb
			# )
		else:
			Utilities.hard_reset()
	except KeyboardInterrupt:
		if clock: clock.stop()
		if buttons: buttons.deinit()
		if adc: adc = None
		if adc_timer: adc_timer.deinit()
