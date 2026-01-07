"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
import network
import socket
from utime import sleep_ms
import smartconfig
from .utilities import Utilities

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
	def set_ap_mode():
		from config import Config

		access_point = network.WLAN(network.AP_IF)

		access_point.active(False)
		access_point.active(True)

		essid = Config.WIFI.AP_SSID
		password = Config.WIFI.AP_PASSWORD

		access_point.ifconfig(Config.WIFI.AP_IFCONFIG)
		access_point.config(
			essid=essid,
			password=password,
			hidden=False,
			authmode=Config.WIFI.AP_AUTHMODE
			# dhcp_hostname=Config.WIFI.AP_HOSTNAME
		)

		print("\naccess point initialized:\n- essid    : {}\n- password : {}".format(essid, "(empty)" if len(password) == 0 else password))
		print("\n", access_point.ifconfig())

	@staticmethod
	def set_sta_mode(essid=None, password='', timeout_sec=600):
		sleep_ms(1000)
		station = network.WLAN(network.STA_IF)
		station.active(False)
		station.active(True)

		using_smartconfig = False

		print("\nConnecting to network...")

		if not station.isconnected():
			if not essid:
				try:
					import sta_config
					essid = sta_config.essid
					password = sta_config.password
				except ImportError:
					print('Start smartconfig...')
					smartconfig.start()

					while not smartconfig.success():
						sleep_ms(500)

					essid, password, _ = smartconfig.info()
					using_smartconfig = True

					print(f'-- Got info, essid={essid}, password={password}')

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

		if status_code == WifiHandler.STATION_CONNECTED and using_smartconfig:
			Utilities.output_sta_config_file(essid, password)
			# WifiHandler.__send_ack(station.ifconfig()[0])

		return status_code

	@staticmethod
	def __send_ack(local_ip):
		udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		token = smartconfig.info()[2].to_bytes(1, 'little') + WifiHandler.get_mac_address()
		for _ in range(30):
			sleep_ms(100)
			try:
				print(udp.sendto(token, ('255.255.255.255', 10000)))
			except OSError:
				pass

	@staticmethod
	def is_sta_connected():
		station = network.WLAN(network.STA_IF)

		return station.isconnected()

	@staticmethod
	def get_mac_address():
		station = network.WLAN(network.STA_IF)
		return station.config('mac')

		# return "".join(['%02X' % i for i in station.config('mac')]).lower()
