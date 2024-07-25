"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-research
"""
from machine import reset
from config import Config
from wifihandler import WifiHandler
from matrix_clock import MatrixClock


clock = MatrixClock()

if __name__ == '__main__':
	try:
		if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode(Config.WIFI.SSID, Config.WIFI.PASSWORD):
			clock.mode = MatrixClock.MODE_TIME
			clock.start()
		else:
			reset()
	except KeyboardInterrupt:
		clock.stop()
