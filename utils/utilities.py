"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
import utime
import ntptime
import network
from machine import RTC

ntptime.host = 'ntp1.aliyun.com'
# ntptime.host = 'ntp.ntsc.ac.cn'
ntptime.timeout = 2


class Utilities(object):
	@staticmethod
	def import_config():
		try:
			from config import Config
		except ImportError:
			Config = __import__('config').Config

		return Config

	@staticmethod
	def soft_reset():
		from sys import exit
		exit()

	@staticmethod
	def hard_reset():
		from machine import reset
		reset()

	@staticmethod
	def sync_time(retry=5) -> bool:
		if network.WLAN(network.STA_IF).isconnected():
			TIMEZONE = Utilities.import_config().TIMEZONE

			print('syncing time...')

			for _ in range(retry):
				try:
					ntptime.settime()
					time = utime.localtime() # (year, month, mday, hour, minute, second, weekday, yearday)
					RTC().datetime((time[0], time[1], time[2], time[6], time[3] + TIMEZONE, time[4], time[5], 0))
					time = utime.localtime()
					print(f'- success: {time[0]}-{time[1]:02d}-{time[2]:02d} {time[3]:02d}:{time[4]:02d}:{time[5]:02d}')
					return True
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
				Utilities.hard_reset()
			else:
				print(f'- Cannot reach ntp host: {ntptime.host}, sync time failed')
				time = utime.localtime()
				print(f'- RTC: {time[0]}-{time[1]:02d}-{time[2]:02d} {time[3]:02d}:{time[4]:02d}:{time[5]:02d}')
		else:
			print('- No wifi connected, sync time cancelled')

		return False


if __name__ == '__main__':
	from utils.wifihandler import WifiHandler

	print('connecting to internet...')
	if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode(timeout_sec=120):
		Utilities.sync_time(3)
	else:
		Utilities.hard_reset()
