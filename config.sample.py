"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
class Config(object):
	class WIFI(object):
		SSID = ''
		PASSWORD = ''


	class PINS(object):
		HSPI_MOSI = 13
		VSPI_MOSI = 23


	class KEYS(object):
		KEY_1 = 22
		KEY_2 = 21
		KEY_3 = 5
		KEY_4 = 4

		KEY_LIST = (KEY_1, KEY_2, KEY_3, KEY_4)

		KEY_MAP = {
			KEY_1: 1,
			KEY_2: 2,
			KEY_3: 3,
			KEY_4: 4
		}


	class Colors(object):
		BLACK = (0, 0, 0)
		WHITE = (128, 128, 128)
		RED = (255, 0, 0)
		BLUE = (0, 0, 255)
		GREEN = (0, 255, 0)
		GREEN_MEDIUM = (128, 128, 0)
		GREEN_LOW = (0, 60, 60)
