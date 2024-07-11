"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
import network
from utime import sleep_ms

__station_status_message = {
	network.STAT_IDLE: "network idle",
	network.STAT_CONNECTING: "",
	network.STAT_GOT_IP: "Connected",
	network.STAT_NO_AP_FOUND: "could not found ap",
	network.STAT_WRONG_PASSWORD: "wrong password given",
	network.STAT_BEACON_TIMEOUT: "beacon timeout",
	network.STAT_ASSOC_FAIL: "assoc fail",
	network.STAT_HANDSHAKE_TIMEOUT: "handshake timeout"
}


class WifiHandler(object):
	AP_MODE = 0
	STA_MODE = 1
	STATION_CONNECTED = network.STAT_GOT_IP

	def __init__(self):
		pass

	@staticmethod
	def set_ap_status(active:bool):
		access_point = network.WLAN(network.AP_IF)
		access_point.active(active)

	@staticmethod
	def set_sta_status(active:bool):
		station = network.WLAN(network.STA_IF)
		station.active(active)

	@staticmethod
	def set_sta_mode(essid, password, timeout_sec=600):
		station = network.WLAN(network.STA_IF)

		print("\nConnecting to network...")

		if not station.isconnected():
			station.active(True)
			station.connect(essid, password)

			retry_count = 0
			while not station.isconnected():
				if timeout_sec > 0:
					if retry_count >= timeout_sec * 2:
						break

				result_code = station.status()

				if result_code == network.STAT_IDLE or\
					result_code == network.STAT_GOT_IP or\
					result_code == network.STAT_NO_AP_FOUND or\
					result_code == network.STAT_WRONG_PASSWORD:
					break
				elif result_code == network.STAT_CONNECTING:
					pass

				retry_count += 1
				sleep_ms(500)

		status_code = station.status()

		print(__station_status_message[status_code])
		print(station.ifconfig())

		return status_code

	@staticmethod
	def is_sta_connected():
		station = network.WLAN(network.STA_IF)

		return station.isconnected()
