"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
__version__ = '0.1'
__version_info__ = (0, 1)
print('module matrix_clock version:', __version__)


#region import modules
from machine import RTC
import utime
import gc

try:
	from .ws2812 import WS2812
except ImportError:
	from matrix.ws2812 import WS2812

from matrix.animation import Animation
from drivers.photoresistor import Photoresistor
from utils.wifihandler import WifiHandler
from utils.utilities import Utilities

try:
	from utils.dispatcher import Dispatcher
except ImportError:
	from dispatcher import Dispatcher
#endregion import modules


CONFIG = Utilities.import_config()


class DateTime(object):
	def __init__(self):
		self.__year =\
		self.__month =\
		self.__day =\
		self.__hour =\
		self.__minute =\
		self.__second =\
		self.__weekday = None

	def first_day_of_month(self) -> int:
		'''获取当月第一天的星期数 (0~6)'''
		self.now()
		return utime.localtime(utime.mktime((self.__year, self.__month, 1, 0, 0, 0, 0, 0)))[6]

	def milliseconds_until_next_minute(self) -> int:
		'''获取到下一分钟之前的毫秒数'''
		self.now()
		return (utime.mktime((self.__year, self.__month, self.__day, self.__hour, self.__minute + 1, 0, 0, 0)) - utime.time()) * 1000

	def milliseconds_until_next_hour(self) -> int:
		'''获取到下一个整点之前的毫秒数'''
		self.now()
		return (utime.mktime((self.__year, self.__month, self.__day, self.__hour + 1, 0, 0, 0, 0)) - utime.time()) * 1000

	def milliseconds_until_midnight(self) -> int:
		'''获取到第二天零点之前的毫秒数'''
		self.now()
		return (utime.mktime((self.__year, self.__month, self.__day + 1, 0, 0, 0, 0, 0)) - utime.time()) * 1000

	def is_leap_year(self) -> bool:
		'''判断今年是否为闰年'''
		self.now()
		return (self.__year % 4 == 0 and self.__year % 100 != 0) or self.__year % 400 == 0

	def format_ms(self, seconds) -> str:
		'''将毫秒数转换为可读时间'''
		seconds //= 1000
		second = seconds % 60
		minutes = (seconds - second) // 60
		minute = minutes % 60
		hour = (minutes - minute) // 60

		return f'{hour:02d}:{minute:02d}:{second:02d}'

	def now(self) -> None:
		'''获取当前系统时间'''
		self.__year,\
		self.__month,\
		self.__day,\
		self.__hour,\
		self.__minute,\
		self.__second,\
		self.__weekday,\
		_ = utime.localtime() # (year, month, mday, hour, minute, second, weekday, yearday)

	def __str__(self):
		self.now()
		weekday = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
		return f'{self.__year}-{self.__month:02d}-{self.__day:02d} {self.__hour:02d}:{self.__minute:02d}:{self.__second:02d} ({weekday[self.__weekday]})'


#region matrix model classes
class ModelClock(object):
	'''
	时钟模式，分区显示当前时间的时、分信息
	'''
	# Led 点阵分区列表
	HOUR_TENS_RANGE = (range(0, 5), range(6, 11), range(12, 17))
	HOUR_ONES_RANGE = (range(24, 29), range(30, 35), range(36, 41))
	MINUTE_TENS_RANGE = range(48, 53)
	MINUTE_ONES_RANGE = (5, 11, 17, 23, 29, 35, 41, 47, 53)

	# 字形列表
	NUMBERS_GLYPH = {
		'0': 0x7e3f, # '111111000111111'
		'1': 0x27e1, # '010011111100001'
		'2': 0x5ebd, # '101111010111101'
		'3': 0x56bf, # '101011010111111'
		'4': 0x709f, # '111000010011111'
		'5': 0x76b7, # '111011010110111'
		'6': 0x7eb7, # '111111010110111'
		'7': 0x421f, # '100001000011111'
		'8': 0x7ebf, # '111111010111111'
		'9': 0x76bf, # '111011010111111'
	}

	def __init__(self):
		self.hour_tens_list = []
		self.hour_ones_list = []
		self.minute_tens_list = list(ModelClock.MINUTE_TENS_RANGE)
		self.minute_ones_list = list(ModelClock.MINUTE_ONES_RANGE)

		self.__fill_range_list()

	def __fill_range_list(self):
		for _ in ModelClock.HOUR_TENS_RANGE:
			self.hour_tens_list += list(_)
		for _ in ModelClock.HOUR_ONES_RANGE:
			self.hour_ones_list += list(_)


class ModelCalendar_1(object):
	'''
	台历模式1，分区显示当前日期的月、日、周信息，日期用数字展示
	'''
	# Led 点阵分区列表
	DAY_TENS_RANGE = (range(1, 6), range(7, 12), range(13, 18))
	DAY_ONES_RANGE = (range(25, 30), range(31, 36), range(37, 42))
	MONTH_RANGE = (range(48, 54), range(42, 48))
	WEEKDAY_RANGE = (0, 6, 12, 18, 24, 30, 36)

	# 字形列表
	NUMBERS_GLYPH = {
		'0': 0x7e3f, # '111111000111111'
		'1': 0x27e1, # '010011111100001'
		'2': 0x5ebd, # '101111010111101'
		'3': 0x56bf, # '101011010111111'
		'4': 0x709f, # '111000010011111'
		'5': 0x76b7, # '111011010110111'
		'6': 0x7eb7, # '111111010110111'
		'7': 0x421f, # '100001000011111'
		'8': 0x7ebf, # '111111010111111'
		'9': 0x76bf, # '111011010111111'
	}

	def __init__(self):
		self.__day_tens_list = []
		self.__day_ones_list = []
		self.__month_list = []
		self.__weekday_list = list(ModelCalendar_1.WEEKDAY_RANGE)

		self.__fill_range_list()

	def __fill_range_list(self):
		for _ in ModelCalendar_1.DAY_TENS_RANGE:
			self.__day_tens_list += list(_)
		for _ in ModelCalendar_1.DAY_ONES_RANGE:
			self.__day_ones_list += list(_)
		for _ in ModelCalendar_1.MONTH_RANGE:
			self.__month_list += list(_)


class ModelCalendar_2(object):
	'''
	台历模式2，分区显示当前日期的月、日、周信息，日期全部展示，需要额外的面板
	'''
	# Led 点阵分区列表
	DAYS_RANGE = (
					   25, 31, 37,
		2,  8, 14, 20, 26, 32, 38,
		3,  9, 15, 21, 27, 33, 39,
		4, 10, 16, 22, 28, 34, 40,
		5, 11, 17, 23, 29, 35, 41
	)
	MONTH_RANGE = (42, 48, 43, 49, 44, 50, 45, 51, 46, 52, 47, 53)
	WEEKDAY_RANGE = (0, 6, 12, 18, 24, 30, 36)

	def __init__(self):
		self.__days_list = list(ModelCalendar_2.DAYS_RANGE)
		self.__month_list = list(ModelCalendar_2.MONTH_RANGE)
		self.__weekday_list = list(ModelCalendar_2.WEEKDAY_RANGE)
#endregion matrix model classes


class MatrixClock(WS2812, DateTime):
	MATRIX_MODE_FILENAME = 'matrix_mode.py'
	MATRIX_MODE_IMPORT_NAME = MATRIX_MODE_FILENAME.split('.')[0]

	MODE_CLOCK      = 0 # 时钟模式
	MODE_CALENDAR_1 = 1 # 台历模式1，数显日期
	MODE_CALENDAR_2 = 2 # 台历模式2，单独显示日期，需要额外的面板

	MODE_LIST = {
		MODE_CLOCK     : 'clock',
		MODE_CALENDAR_1: 'calendar_1',
		MODE_CALENDAR_2: 'calendar_2'
	}

	MENU_LIST = {
		MODE_CLOCK     : Animation.MENU_CLOCK,
		MODE_CALENDAR_1: Animation.MENU_CALENDAR_1,
		MODE_CALENDAR_2: Animation.MENU_CALENDAR_2
	}

	BRIGHTNESS_LEVEL = {
		Photoresistor.LEVEL_1: 60,
		Photoresistor.LEVEL_2: 50,
		Photoresistor.LEVEL_3: 40,
		Photoresistor.LEVEL_4: 30,
		Photoresistor.LEVEL_5: 20,
		Photoresistor.LEVEL_6: 10
	}

	def __init__(self):
		WS2812.__init__(self,
			CONFIG.WS2812_MATRIX.WIDTH,
			CONFIG.WS2812_MATRIX.HEIGHT,
			CONFIG.PINS.DIN_MATRIX)
		DateTime.__init__(self)

		self.__tasks     = Dispatcher()
		self.__adc       = Photoresistor(CONFIG.PINS.BRIGHTNESS_ADC)
		self.__animation = Animation()

		# 模式对象实例
		self.__model_clock    = None
		self.__model_calendar = None

		'''
		设备工作模式
		  工作模式就是 MODE_LIST 列出来的三种
		  前两种模式可以临时互相切换显示内容
		  第三种模式需要更换面板所以不能互换
		'''
		self.__working_mode   = self.__get_matrix_mode()
		self.__display_mode   = self.__working_mode
		self.__menu_mode      = False
		self.__last_menu      = self.__working_mode
		self.__last_adc_level = 0     # 记录当前 adc 等级
		self.__last_hour      = 0     # 记录当前小时
		self.__last_minute    = 0     # 记录当前分钟
		self.__started        = False # 设备运行状态
		self.__time_synced    = False # 校时成功状态
		self.__hourly_chime   = True  # 整点报时开关
		self.__powered_on     = True  # 屏幕显示开关

		# 定时器任务
		self.__task_sync_ntp_time    = lambda: self.__sync_time_cb()
		self.__task_auto_brightness  = lambda: self.__auto_brightness_cb()
		self.__task_refresh_time     = lambda: self.__refresh_time_cb()
		self.__task_refresh_calendar = lambda: self.__refresh_calendar_cb()
		self.__task_show_animation   = lambda: self.__show_animation_cb()
		self.__task_switch_display   = lambda: self.__switch_display_cb()

		self.switch_mode(self.mode)

		self.__auto_brightness_cb()
		self.__tasks.add_work(self.__task_auto_brightness, CONFIG.PERIOD.UPDATE_ADC_MS)

	def start(self):
		print(f'starting {MatrixClock.MODE_LIST[self.mode]} mode')

		if not self.__time_synced:
			self.__sync_time_cb()

		self.__auto_brightness_cb()
		self.__tasks.add_work(self.__task_auto_brightness, CONFIG.PERIOD.UPDATE_ADC_MS)

		self.__started = True

		if self.mode == MatrixClock.MODE_CLOCK:
			self.__refresh_time_cb()
		elif self.mode == MatrixClock.MODE_CALENDAR_1:
			self.__refresh_calendar_cb()
		elif self.mode == MatrixClock.MODE_CALENDAR_2:
			self.__refresh_calendar_cb()

	def stop(self):
		self.__started = False

		self.__tasks.del_works()
		self.clean()

	def start_stop_menu(self, save:bool=True):
		'''进入/退出菜单模式'''
		if self.__menu_mode:
			if save and self.mode != self.__last_menu:
				self.switch_mode(self.__last_menu)
				self.__output_matrix_mode_file()

			self.__menu_mode = False
			self.stop()
			self.start()
		else:
			self.__menu_mode = True
			self.stop()
			self.switch_menu(True)

	def show_content(self):
		'''显示当前工作模式下需要展示的内容'''
		if not self.__powered_on or not self.__started:
			return

		print(f'showing {MatrixClock.MODE_LIST[self.mode]} content')

		if self.mode == MatrixClock.MODE_CLOCK:
			self.show_time()
		elif self.mode == MatrixClock.MODE_CALENDAR_1:
			self.show_calendar_1()
		elif self.mode == MatrixClock.MODE_CALENDAR_2:
			self.show_calendar_2()

	def switch_power(self):
		'''开启/关闭内容显示'''
		self.__powered_on = not self.__powered_on

		self.show_content() if self.__powered_on else self.clean()

	def switch_mode(self, mode):
		'''切换工作模式，切换后需要手动调用 start() 函数'''
		self.mode = mode
		suffix = f' for {self.format_ms(CONFIG.PERIOD.SWITCH_DISPLAY_MS)}' if self.mode != self.__display_mode else ''

		print(f'switching to {MatrixClock.MODE_LIST[self.mode]} mode{suffix}')

		self.stop()

		self.__model_clock = None
		self.__model_calendar = None

		if self.mode == MatrixClock.MODE_CLOCK:
			self.__model_clock = ModelClock()
		elif self.mode == MatrixClock.MODE_CALENDAR_1:
			self.__model_calendar = ModelCalendar_1()
		elif self.mode == MatrixClock.MODE_CALENDAR_2:
			self.__model_calendar = ModelCalendar_2()

		gc.collect()

	def switch_menu(self, first=False):
		'''切换显示菜单'''
		if not self.__menu_mode:
			return

		if not first:
			self.__last_menu = (self.__last_menu + 1) % len(MatrixClock.MENU_LIST)

		self.__animation.select_animation(
			MatrixClock.MENU_LIST[self.__last_menu],
			self.convert_color(CONFIG.COLORS.SKYBLUE)
		)

		self.__tasks.add_work(self.__task_show_animation, self.__animation.period)

	def switch_display_mode(self):
		'''临时切换显示时钟和台历1'''
		self.__switch_display_cb()

	def show_animation(self):
		'''播放配网/联网简易动画'''
		animation = None
		colors = None

		try:
			__import__(WifiHandler.STA_CONFIG_IMPORT_NAME)

			animation = Animation.CONNECT_WIFI
			colors = self.convert_color(CONFIG.COLORS.WHITE)
		except ImportError:
			animation = Animation.CONFIG_WIFI

			if WifiHandler.is_ble_mode():
				colors = (
					self.convert_color(CONFIG.COLORS.BLACK),
					self.convert_color(CONFIG.COLORS.SKYBLUE)
				)
			else:
				colors = (
					self.convert_color(CONFIG.COLORS.BLACK),
					self.convert_color(CONFIG.COLORS.LIGHTGREEN)
				)

		self.__animation.select_animation(animation, colors)
		self.__tasks.add_work(self.__task_show_animation, self.__animation.period)

	def show_blink(self):
		'''用于整点报时的闪烁'''
		if not self.__powered_on:
			return

		color = CONFIG.COLORS.WHITE

		self.fill(color)
		utime.sleep(0.1)
		self.clean()
		utime.sleep(0.1)
		self.fill(color)
		utime.sleep(0.1)
		self.clean()
		utime.sleep(0.1)
		self.fill(color)
		utime.sleep(0.5)
		self.clean()

		self.show_content()

	#region model clock related function
	def show_time(self):
		'''刷新时钟内容'''
		self.now()

		is_new_hour = False

		if self.__last_hour != self.__hour and self.__minute == 0:
			self.__last_hour = self.__hour
			is_new_hour = True

			if self.hourly_chime:
				self.show_blink()

		self.__set_hour()
		self.__set_minute(is_new_hour)
		self.show()

	def __set_hour(self):
		hour = self.__zfill_2int(self.__hour)
		hour_tens = self.__zfile_15bin(ModelClock.NUMBERS_GLYPH[hour[0]])
		hour_ones = self.__zfile_15bin(ModelClock.NUMBERS_GLYPH[hour[1]])

		hour_color = self.convert_color(CONFIG.COLORS.TIME_HOUR)

		for index, bit in enumerate(hour_tens):
			self.__neopixel[self.__model_clock.hour_tens_list[index]] = hour_color if bit == '1' else CONFIG.COLORS.BLACK

		for index, bit in enumerate(hour_ones):
			self.__neopixel[self.__model_clock.hour_ones_list[index]] = hour_color if bit == '1' else CONFIG.COLORS.BLACK

	def __set_minute(self, is_new_hour:bool):
		if is_new_hour:
			def clean_minute_tens():
				for index in range(4, -1, -1):
					self.__neopixel[self.__model_clock.minute_tens_list[index]] = CONFIG.COLORS.BLACK
					yield

			if not self.hourly_chime:
				# 以动画效果消除分钟
				minute_tens_gen = clean_minute_tens()
				for index in range(8, -1, -1):
					try:
						next(minute_tens_gen)
					except StopIteration:
						pass

					self.__neopixel[self.__model_clock.minute_ones_list[index]] = CONFIG.COLORS.BLACK
					utime.sleep(0.05)
					self.show()
		else:
			minute = self.__zfill_2int(self.__minute)
			minute_tens = int(minute[0])
			minute_ones = int(minute[1])

			minute_tens_color = self.convert_color(CONFIG.COLORS.TIME_MINUTE_TENS)
			minute_ones_colors = {
				0: self.convert_color(CONFIG.COLORS.TIME_MINUTE_ONES_1),
				1: self.convert_color(CONFIG.COLORS.TIME_MINUTE_ONES_2),
				2: self.convert_color(CONFIG.COLORS.TIME_MINUTE_ONES_3)
			}

			for count, index in enumerate(self.__model_clock.minute_tens_list):
				self.__neopixel[index] = minute_tens_color if count < minute_tens else CONFIG.COLORS.BLACK

			if self.__last_minute != self.__minute:
				self.__last_minute = self.__minute

				if minute_ones == 0:
					for index in range(8, -1, -1):
						self.__neopixel[self.__model_clock.minute_ones_list[index]] = CONFIG.COLORS.BLACK
						utime.sleep(0.05)
						self.show()

			for count, index in enumerate(self.__model_clock.minute_ones_list):
				'''
				假设有一组连续的数字，把它们每 n 个分为一组，随意指定一个数字 x，求 x 在哪一组？
				公式为：int((x + 1) // (n + 0.1))
				感谢 Jason 提供的算法
				'''
				minute_ones_color = minute_ones_colors[int((count + 1) // 3.1)]
				self.__neopixel[index] = minute_ones_color if count < minute_ones else CONFIG.COLORS.BLACK
	#endregion model clock related function


	#region model calendar_1 related function
	def show_calendar_1(self):
		'''刷新日历模式一显示内容'''
		self.now()
		self.__set_day_1()
		self.__set_weekday_month_1()
		self.show()

	def __set_day_1(self):
		day = self.__zfill_2int(self.__day)
		day_tens = self.__zfile_15bin(ModelCalendar_1.NUMBERS_GLYPH[day[0]])
		day_ones = self.__zfile_15bin(ModelCalendar_1.NUMBERS_GLYPH[day[1]])

		day_color = self.convert_color(CONFIG.COLORS.DATE_DAY)

		for index, bit in enumerate(day_tens):
			self.__neopixel[self.__model_calendar.__day_tens_list[index]] = day_color if bit == '1' else CONFIG.COLORS.BLACK

		for index, bit in enumerate(day_ones):
			self.__neopixel[self.__model_calendar.__day_ones_list[index]] = day_color if bit == '1' else CONFIG.COLORS.BLACK

	def __set_weekday_month_1(self):
		for index in self.__model_calendar.__weekday_list:
			self.__neopixel[index] = CONFIG.COLORS.DATE_WEEKDAY_BG

		self.__neopixel[self.__model_calendar.__weekday_list[self.__weekday]] = self.convert_color(CONFIG.COLORS.DATE_WEEKDAY)

		month_colors = {
			0: self.convert_color(CONFIG.COLORS.DATE_MONTH_1),
			1: self.convert_color(CONFIG.COLORS.DATE_MONTH_2),
			2: self.convert_color(CONFIG.COLORS.DATE_MONTH_3),
			3: self.convert_color(CONFIG.COLORS.DATE_MONTH_4)
		}

		for count, index in enumerate(self.__model_calendar.__month_list):
			month_color = month_colors[int((count + 1) // 3.1)]
			self.__neopixel[index] = month_color if count < self.__month else CONFIG.COLORS.DATE_MONTH_BG
	#endregion model calendar_1 related function


	#region model calendar_2 related function
	def show_calendar_2(self):
		'''刷新日历模式二显示内容'''
		self.now()
		self.__set_day_2()
		self.__set_weekday_month_2()
		self.show()

	def __set_day_2(self):
		for index in self.__model_calendar.__days_list:
			self.__neopixel[index] = CONFIG.COLORS.DATE_DAYS_BG

		self.__neopixel[self.__model_calendar.__days_list[self.__day - 1]] = self.convert_color(CONFIG.COLORS.DATE_DAY)

	def __set_weekday_month_2(self):
		for index in self.__model_calendar.__weekday_list:
			self.__neopixel[index] = CONFIG.COLORS.DATE_WEEKDAY_BG

		self.__neopixel[self.__model_calendar.__weekday_list[self.__weekday]] = self.convert_color(CONFIG.COLORS.DATE_WEEKDAY)

		for index in self.__model_calendar.__month_list:
			self.__neopixel[index] = CONFIG.COLORS.DATE_MONTH_BG

		self.__neopixel[self.__model_calendar.__month_list[self.__month - 1]] = self.convert_color(CONFIG.COLORS.DATE_MONTH)
	#endregion model calendar_2 related function


	#region callbacks function
	def __sync_time_cb(self):
		'''联网校时回调函数'''
		self.__time_synced = Utilities.sync_time()
		self.__tasks.add_work(self.__task_sync_ntp_time, self.milliseconds_until_next_hour())

		print('sync time after:', self.format_ms(self.milliseconds_until_next_hour()))

	def __auto_brightness_cb(self):
		'''自动亮度回调函数'''
		adc_level = self.__adc.level

		if self.__last_adc_level == adc_level:
			return

		self.__last_adc_level = adc_level
		self.brightness = MatrixClock.BRIGHTNESS_LEVEL[adc_level]

		self.show_content()
		print(f'set brightness level to {adc_level} ({self.brightness}%)')

	def __refresh_time_cb(self):
		'''刷新时间显示回调函数'''
		self.show_content()
		self.__tasks.add_work(self.__task_refresh_time, self.milliseconds_until_next_minute())

	def __refresh_calendar_cb(self):
		'''刷新日历显示回调函数'''
		self.show_content()
		self.__tasks.add_work(self.__task_refresh_calendar, self.milliseconds_until_next_hour())

	def __show_animation_cb(self):
		'''显示联网动画'''
		remains, frame, color = self.__animation.get_frame_and_color()

		for index, bit in enumerate(self.__zfill_54bin(frame)):
			self.__neopixel[index] = color if bit == '1' else CONFIG.COLORS.BLACK

		self.show()

		if not self.__animation.loops and remains == 0:
			self.__tasks.del_work(self.__task_show_animation)

	def __switch_display_cb(self):
		if self.mode == MatrixClock.MODE_CALENDAR_2:
			return

		if self.mode == MatrixClock.MODE_CLOCK:
			self.switch_mode(MatrixClock.MODE_CALENDAR_1)
		elif self.mode == MatrixClock.MODE_CALENDAR_1:
			self.switch_mode(MatrixClock.MODE_CLOCK)

		self.start()

		if self.mode == self.__display_mode:
			self.__tasks.del_work(self.__task_switch_display)
		else:
			self.__tasks.add_work(self.__task_switch_display, CONFIG.PERIOD.SWITCH_DISPLAY_MS)
	#endregion callbacks function


	#region tools function
	def __zfill_2int(self, value:int):
		'''将时分、日期填充为 2 位数字符串'''
		return f'{value:0>2}'

	def __zfile_15bin(self, value:int):
		'''将整型转为 15 位二进制字符串'''
		return f'{value:0>15b}'

	def __zfill_54bin(self, value:int):
		'''将整型转为 54 位二进制字符串'''
		return f'{value:0>54b}'

	def __output_matrix_mode_file(self):
		with open(MatrixClock.MATRIX_MODE_FILENAME, 'w') as output:
			output.write(
f'''# automatic generated file
mode = {self.mode} # {MatrixClock.MODE_LIST[self.mode]}
'''
			)

	def __get_matrix_mode(self) -> int:
		mode = MatrixClock.MODE_CLOCK

		try:
			mode = __import__(MatrixClock.MATRIX_MODE_IMPORT_NAME).mode
		except ImportError:
			pass

		return mode

	def set_time(self, minute, second=0):
		# year, month, day, hour, minute, second, weekday, yearday
		time = utime.localtime()
		# year, month, day, weekday, hour, minute, second, subsecond
		RTC().datetime((self.__year, self.__month, self.__day, self.__weekday, self.__hour, minute, second, 0))
		self.show_content()

	def set_month(self, month):
		self.now()
		RTC().datetime((self.__year, month, self.__day, self.__weekday, self.__hour, self.__minute, self.__second, 0))
		self.show_content()
	#endregion tools function


	#region class properties
	@property
	def mode(self) -> int:
		return self.__working_mode

	@mode.setter
	def mode(self, value:int):
		'''获取/设置当前工作模式'''
		if value in MatrixClock.MODE_LIST.keys():
			self.__working_mode = value

	@property
	def hourly_chime(self) -> bool:
		return self.__hourly_chime

	@hourly_chime.setter
	def hourly_chime(self, value:bool):
		'''获取/设置是否启用整点报时功能'''
		if isinstance(value, bool):
			self.__hourly_chime = value
	#endregion class properties


if __name__ == '__main__':
	matrix = MatrixClock()
	matrix.show_animation()

	if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode():
		matrix.stop()
		matrix.show_blink()
		matrix.start()
