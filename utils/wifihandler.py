"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
import network
import socket
from utime import sleep_ms
import smartconfig


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
	STATION_CONNECTED = network.STAT_GOT_IP
	WIFI_CONFIG_MODE_FILENAME = 'smart.config'
	STA_CONFIG_FILENAME = 'sta_config.py'
	STA_CONFIG_IMPORT_NAME = STA_CONFIG_FILENAME.split('.')[0]

	@staticmethod
	def set_sta_status(active:bool):
		station = network.WLAN(network.STA_IF)
		station.active(active)

	@staticmethod
	def is_sta_connected():
		station = network.WLAN(network.STA_IF)

		return station.isconnected()

	@staticmethod
	def get_mac_address():
		station = network.WLAN(network.STA_IF)
		return station.config('mac')

	@staticmethod
	def set_sta_mode(essid=None, password='', timeout_sec=600):
		sleep_ms(1000)
		station = network.WLAN(network.STA_IF)
		station.active(False)
		station.active(True)

		using_smartconfig = False

		print("\nConnecting to network...")

		if not station.isconnected():
			if essid is None:
				try:
					sta_config = __import__(WifiHandler.STA_CONFIG_IMPORT_NAME)
					essid = sta_config.essid
					password = sta_config.password
				except ImportError:
					if WifiHandler.is_ble_mode():
						try:
							BLEConfig = __import__('./utils/ble_config').BLEConfig
						except ImportError:
							from utils.ble_config import BLEConfig

						print('Start bleconfig...')
						bleconfig = BLEConfig()

						while not bleconfig.success():
							sleep_ms(100)

						essid = bleconfig.ssid
						password = bleconfig.password

						print(f'-- Got info\n    ssid={essid}\n    password={password}')

						WifiHandler.output_sta_config_file(essid, password)
						WifiHandler.hard_reset()
					else:
						print('Start smartconfig...')
						smartconfig.start()

						while not smartconfig.success():
							sleep_ms(100)

						essid, password, sc_type, token = smartconfig.info()
						using_smartconfig = True

						print(f'-- Got info\n    ssid={essid}\n    password={password}\n    type={sc_type}\n    token={token}')

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
			WifiHandler.output_sta_config_file(essid, password)
			WifiHandler.__send_smartconfig_ack(station.ifconfig()[0])

		return status_code

#region SmartConfig related functions
	@staticmethod
	def __send_smartconfig_ack(local_ip):
		udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		token = smartconfig.info()[3].to_bytes(1, 'little') + WifiHandler.get_mac_address()
		port = 10000

		if smartconfig.info()[2] == smartconfig.TYPE_ESPTOUCH:
			token += WifiHandler.inet_pton(local_ip)
			port = 18266

		for _ in range(30):
			sleep_ms(100)
			try:
				udp.sendto(token, ('255.255.255.255', port))
			except OSError:
				pass
		print('ack was sent')

	@staticmethod
	def inet_pton(ip_str:str):
		'''
		字符串 IP 地址转字节串
		'''
		result = b''
		ip_seg = ip_str.split('.')

		for seg in ip_seg:
			result += int(seg).to_bytes(1, 'little')

		return result

	@staticmethod
	def output_sta_config_file(essid, password):
		with open(WifiHandler.STA_CONFIG_FILENAME, 'w') as output:
			output.write(
f'''# automatic generated file
essid = '{essid}'
password = '{password}'
'''
			)
	
	@staticmethod
	def delete_sta_config_file():
		import os
		try:
			os.remove(WifiHandler.STA_CONFIG_FILENAME)
		except:
			pass

	@staticmethod
	def output_wifi_mode_file():
		with open(WifiHandler.WIFI_CONFIG_MODE_FILENAME, 'w') as file:
			file.write('# enter smartconfig mode if this file exists')

	@staticmethod
	def delete_wifi_mode_file():
		import os
		try:
			os.remove(WifiHandler.WIFI_CONFIG_MODE_FILENAME)
		except:
			pass

	@staticmethod
	def is_ble_mode():
		import os
		try:
			os.stat(WifiHandler.WIFI_CONFIG_MODE_FILENAME)
			return False
		except:
			return True

	@staticmethod
	def hard_reset():
		from machine import reset
		reset()
#endregion
