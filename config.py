"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from utils.utilities import Utilities
import esp
import esp32

esp.osdebug(None) # 注释此行可显示详细调试信息

esp32c3 = Utilities.is_esp32c3()

# channel 0/1 for esp32c3
if esp32c3: esp32.RMT.bitstream_channel(0)


class Config(object):
	class BRIGHTNESS(object):
		# 根据实际情况设置亮度最大值，取值范围 (1~200)
		MAX = 150


	class PINS(object):
		ADC = 1
		DIN = 7 if esp32c3 else 13


	class KEYS(object):
		KEY_1 = 2 if esp32c3 else 22
		KEY_2 = 3 if esp32c3 else 21
		KEY_3 = 4 if esp32c3 else 5
		KEY_4 = 5 if esp32c3 else 4
		KEY_TEST = 6 if esp32c3 else 12
		KEY_BOOT = 9 if esp32c3 else 0

		KEY_LIST = (KEY_1, KEY_2, KEY_3, KEY_4, KEY_TEST, KEY_BOOT)

		KEY_MAP = {
			KEY_1: 1,
			KEY_2: 2,
			KEY_3: 3,
			KEY_4: 4,
			KEY_TEST: 'TEST',
			KEY_BOOT: 'BOOT'
		}


	class PERIOD(object):
		CLOCK_MS = 1000 * 5
		CLOCK_SYNC = int(3600 * 1000 / CLOCK_MS)
		ADC_MS = 1000 * 3


	class MATRIX(object):
		HEIGHT = ROWS = 6
		WIDTH = COLUMNS = 9
		VERTICAL = True


	class Colors(object):
		BLACK = (0, 0, 0)
		WHITE = (255, 255, 255)
		RED = (255, 0, 0)
		BLUE = (40, 40, 219)
		GREEN = (247, 24, 255)			# minute 7~9
		GREEN_MEDIUM = (55, 231, 253)	# minute 4~6
		GREEN_LOW = (164, 229, 1)		# minute 1~3


	# class WIFI(object):
	# 	AP_SSID = 'Matrix Led Clock'
	# 	AP_PASSWORD = ''
	# 	AP_AUTHMODE = 0
	# 	AP_HOST = "192.168.66.1"
	# 	AP_PORT = 80
	# 	AP_IFCONFIG = (AP_HOST, "255.255.255.0", AP_HOST, AP_HOST)
	# 	AP_PORTAL = {'*': AP_HOST}
