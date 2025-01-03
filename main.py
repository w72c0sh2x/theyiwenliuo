"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-research
"""
from machine import reset
from utils.wifihandler import WifiHandler

clock = None


if __name__ == '__main__':
	try:
		if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode():
			from matrix.matrix_clock import MatrixClock

			clock = MatrixClock()
			clock.mode = MatrixClock.MODE_TIME
			clock.start()
		else:
			reset()
	except KeyboardInterrupt:
		if clock:
			clock.stop()
