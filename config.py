"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
__version__ = '0.1'
__version_info__ = (0, 1)
print('module config version:', __version__)


import esp
import esp32


# esp.osdebug(None) # 注释此行可显示详细调试信息

# channel 0/1 for esp32c3
esp32.RMT.bitstream_channel(0)


class Config(object):
	TIMEZONE = 8

	class BRIGHTNESS(object):
		# 根据实际情况设置亮度最大值百分比，取值范围 (1~100)
		MAX = 80


	class PINS(object):
		BRIGHTNESS_ADC = 1
		DIN_MATRIX	   = 7


	class KEYS(object):
		KEY_1	 = 2
		KEY_2	 = 3
		KEY_3	 = 4
		KEY_4	 = 5
		KEY_TEST = 6
		KEY_BOOT = 9

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
		UPDATE_ADC_MS = 500 # 光敏电阻检测间隔时间


	class WS2812_MATRIX(object):
		HEIGHT = ROWS = 6
		WIDTH = COLUMNS = 9


	# https://www.colorhexa.com/color-names
	# https://www.rapidtables.com/web/color/RGB_Color.html
	class COLORS(object):
		BLACK        = (0, 0, 0)
		WHITE        = (255, 255, 255)
		BLUE         = (2, 79, 195)
		DARKGRAY     = (54, 54, 54)
		SKYBLUE      = (9, 171, 255)
		LIGHTGREEN   = (121, 234, 0)
		YELLOWGREEN  = (154, 205, 50)
		TURQUOISE    = (64, 224, 208)
		MEDIUMORCHID = (186, 85, 211)
		PINEGREEN    = (1, 121, 111)
		ALMOSTBLACK  = (2, 2, 2)
		ALMOSTGREEN  = (2, 3, 0)

		# 时间显示相关颜色
		TIME_HOUR          = WHITE
		TIME_MINUTE_TENS   = SKYBLUE
		TIME_MINUTE_ONES_1 = YELLOWGREEN
		TIME_MINUTE_ONES_2 = TURQUOISE
		TIME_MINUTE_ONES_3 = MEDIUMORCHID

		# 日期显示相关颜色
		DATE_DAY        = WHITE
		DATE_DAYS_BG    = ALMOSTBLACK
		DATE_WEEKDAY    = LIGHTGREEN
		DATE_WEEKDAY_BG = ALMOSTGREEN
		DATE_MONTH      = SKYBLUE
		DATE_MONTH_BG   = ALMOSTBLACK
		DATE_MONTH_1    = YELLOWGREEN
		DATE_MONTH_2    = TURQUOISE
		DATE_MONTH_3    = MEDIUMORCHID
		DATE_MONTH_4    = PINEGREEN
