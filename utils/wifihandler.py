"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
import network
import socket
import utime
import ntptime
import smartconfig
from machine import RTC, reset

TIMEZONE = 8
ntptime.host = 'ntp.ntsc.ac.cn'
# ntptime.NTP_DELTA -= TIMEZONE * 60 * 60
# ntptime.host = 'ntp1.aliyun.com'

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
	STA_CONFIG_FILENAME = 'sta_config.py'
	STA_CONFIG_IMPORT_NAME = STA_CONFIG_FILENAME.split('.')[0]
	INTERVAL_FROM_1970_TO_2000 = 946_656_000 # in second

	@staticmethod
	def set_sta_status(active:bool):
		station = network.WLAN(network.STA_IF)
		station.active(active)

	@staticmethod
	def set_sta_mode(essid=None, password='', timeout_sec=600):
		utime.sleep_ms(1000)
		station = network.WLAN(network.STA_IF)
		station.active(False)
		station.active(True)

		using_smartconfig = False

		print("\nConnecting to network...")

		if not station.isconnected():
			if not essid:
				try:
					sta_config = __import__(WifiHandler.STA_CONFIG_IMPORT_NAME)
					essid = sta_config.essid
					password = sta_config.password
				except ImportError:
					print('Start smartconfig...')
					smartconfig.start()

					while not smartconfig.success():
						utime.sleep_ms(500)

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
				utime.sleep_ms(500)

		status_code = station.status()

		print(__station_status_message[status_code])
		print(station.ifconfig())

		if status_code == WifiHandler.STATION_CONNECTED and using_smartconfig:
			WifiHandler.output_sta_config_file(essid, password)
			WifiHandler.__send_smartconfig_ack(station.ifconfig()[0])

		return status_code

	@staticmethod
	def sync_time(retry=5):
		if WifiHandler.is_sta_connected():
			print('sync time')

			for _ in range(retry):
				try:
					ntptime.settime()
					time = utime.localtime()
					RTC().datetime((time[0], time[1], time[2], time[6] + 1, time[3] + TIMEZONE, time[4], time[5], 0))
					time = utime.localtime()
					print(f'{time[0]}-{time[1]}-{time[2]} {time[3]}:{time[4]}:{time[5]}')
					return
				except OSError as ose:
					if str(ose) == '[Errno 116] ETIMEDOUT':
						pass
					else:
						print(ose)
				except Exception as e:
					print(e)

				utime.sleep(0.2)

			if utime.time() < 60 * 60 * 2:
				# first time sync time failed, reset
				reset()
			else:
				print(f'Cannot reach ntp host: {ntptime.host}, sync time failed')
				time = utime.localtime()
				print(f'RTC: {time[0]}-{time[1]}-{time[2]} {time[3]}:{time[4]}:{time[5]}')
		else:
			print('No wifi connected, sync time cancelled')

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
			utime.sleep_ms(100)
			try:
				udp.sendto(token, ('255.255.255.255', port))
			except OSError:
				pass
		print('ack was sent')

	@staticmethod
	def is_sta_connected():
		station = network.WLAN(network.STA_IF)

		return station.isconnected()

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
	def get_mac_address():
		station = network.WLAN(network.STA_IF)
		return station.config('mac')

	@staticmethod
	def output_sta_config_file(essid, password):
		with open(WifiHandler.STA_CONFIG_FILENAME, 'w') as output:
			output.write(
f'''# automatic generated file
essid = '{essid}'
password = '{password}'
'''
			)


if __name__ == '__main__':
	if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode(timeout_sec=120):
		WifiHandler.sync_time()
