"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
__version__ = '0.1.1'
__version_info__ = (0, 1, 1)
print('module animation version:', __version__)


class AnimationException(Exception):
	pass


class Animation(object):
	'''生成简易动画数据'''
	CONFIG_WIFI  = 0 # 配网指示
	CONNECT_WIFI = 1 # 联网指示
	HEARTBEAT    = 2 # 心跳动画
	UPDATING     = 3 # 在线更新动画
	SUCCESS      = 4 # 成功提示动画
	FAILED       = 5 # 失败提示动画

	MENU_CLOCK      = 6 # 时钟菜单
	MENU_CALENDAR_1 = 7 # 台历1菜单
	MENU_CALENDAR_2 = 8 # 台历2菜单
	MENU_UPDATE     = 9 # 在线更新菜单

	DEFAULT_PERIOD = 50
	DEFAULT_STEPS  = 10
	DEFAULT_LOOPS  = True

	ANIMATION_LIST = [
		CONFIG_WIFI,
		CONNECT_WIFI,
		HEARTBEAT,
		MENU_CLOCK,
		MENU_CALENDAR_1,
		MENU_CALENDAR_2,
		MENU_UPDATE,
		UPDATING,
		SUCCESS,
		FAILED
	]

	RESOURCES = {
		# 呼吸效果的配网指示动画
		CONFIG_WIFI: {
			'period': 60,
			'steps' : 20,
			'frames': {
				0: 0x80180380780 # 000000000010000000000110000000001110000000011110000000
			},
		},
		# 动态增加效果的连接指示动画
		CONNECT_WIFI: {
			'period': 200,
			'frames': {
				0: 0x0,           # 000000000000000000000000000000000000000000000000000000
				1: 0x80000000000, # 000000000010000000000000000000000000000000000000000000
				2: 0x80180000000, # 000000000010000000000110000000000000000000000000000000
				3: 0x80180380000, # 000000000010000000000110000000001110000000000000000000
				4: 0x80180380780, # 000000000010000000000110000000001110000000011110000000
			}
		},
		# 心跳动画
		HEARTBEAT: {
			'period': 300,
			'frames': {
				0: 0x850a508000,   # 000000000000001000010100001010010100001000000000000000
				1: 0xc48948c000,   # 000000000000001100010010001001010010001100000000000000
				2: 0x8522448462508 # 001000010100100010010001001000010001100010010100001000
			}
		},
		# 在线更新动画
		UPDATING: {
			'period': 100,
			'loops' : True,
			'frames': {
				0:  0x1000000,     # 000000000000000000000000000001000000000000000000000000
				1:  0x42040000,    # 000000000000000000000001000010000001000000000000000000
				2:  0x1084081000,  # 000000000000000001000010000100000010000001000000000000
				3:  0x2109102000,  # 000000000000000010000100001001000100000010000000000000
				4:  0x4252244000,  # 000000000000000100001001010010001001000100000000000000
				5:  0x94a4489000,  # 000000000000001001010010100100010010001001000000000000
				6:  0x12908912000, # 000000000000010010100100001000100100010010000000000000
				7:  0x24210224000, # 000000000000100100001000010000001000100100000000000000
				8:  0x8420408000,  # 000000000000001000010000100000010000001000000000000000
				9:  0x10800810000, # 000000000000010000100000000000100000010000000000000000
				10: 0x20000020000, # 000000000000100000000000000000000000100000000000000000
				11: 0x0,           # 000000000000000000000000000000000000000000000000000000
			}
		},
		# 成功提示动画
		SUCCESS: {
			'period': 80,
			'loops' : False,
			'frames': {
				0: 0x100000000000, # 000000000100000000000000000000000000000000000000000000
				1: 0x102000000000, # 000000000100000010000000000000000000000000000000000000
				2: 0x102040000000, # 000000000100000010000001000000000000000000000000000000
				3: 0x102042000000, # 000000000100000010000001000010000000000000000000000000
				4: 0x102042100000, # 000000000100000010000001000010000100000000000000000000
				5: 0x102042108000, # 000000000100000010000001000010000100001000000000000000
				6: 0x102042108400, # 000000000100000010000001000010000100001000010000000000
				7: 0x102042108400, # 000000000100000010000001000010000100001000010000000000
				8: 0x102042108400, # 000000000100000010000001000010000100001000010000000000
			}
		},
		# 失败提示动画
		FAILED: {
			'period': 80,
			'loops' : False,
			'frames': {
				0:  0x10000,       # 000000000000000000000000000000000000010000000000000000
				1:  0x210000,      # 000000000000000000000000000000001000010000000000000000
				2:  0x4210000,     # 000000000000000000000000000100001000010000000000000000
				3:  0x84210000,    # 000000000000000000000010000100001000010000000000000000
				4:  0x1084210000,  # 000000000000000001000010000100001000010000000000000000
				5:  0x11084210000, # 000000000000010001000010000100001000010000000000000000
				6:  0x11284210000, # 000000000000010001001010000100001000010000000000000000
				7:  0x11284290000, # 000000000000010001001010000100001010010000000000000000
				8:  0x11284291000, # 000000000000010001001010000100001010010001000000000000
				9:  0x11284291000, # 000000000000010001001010000100001010010001000000000000
				10: 0x11284291000, # 000000000000010001001010000100001010010001000000000000
			}
		},
		# 时钟菜单图标
		MENU_CLOCK: {
			'period': 40,
			'loops' : False,
			'frames': {
				0: 0xc000000000000,  # 001100000000000000000000000000000000000000000000000000
				1: 0x12300000000000, # 010010001100000000000000000000000000000000000000000000
				2: 0x2548c000000000, # 100101010010001100000000000000000000000000000000000000
				3: 0x2d952300000000, # 101101100101010010001100000000000000000000000000000000
				4: 0x21b6548c000000, # 100001101101100101010010001100000000000000000000000000
				5: 0x1286d952300000, # 010010100001101101100101010010001100000000000000000000
				6: 0xc4a1b6548c000,  # 001100010010100001101101100101010010001100000000000000
				7: 0x31286d952300    # 000000001100010010100001101101100101010010001100000000
			}
		},
		# 台历1菜单图标
		MENU_CALENDAR_1: {
			'period': 40,
			'loops' : False,
			'frames': {
				0: 0x1f000000000000, # 011111000000000000000000000000000000000000000000000000
				1: 0x217c0000000000, # 100001011111000000000000000000000000000000000000000000
				2: 0x2385f000000000, # 100011100001011111000000000000000000000000000000000000
				3: 0x2f8e17c0000000, # 101111100011100001011111000000000000000000000000000000
				4: 0x2bbe385f000000, # 101011101111100011100001011111000000000000000000000000
				5: 0x21aef8e17c0000, # 100001101011101111100011100001011111000000000000000000
				6: 0x1f86bbe385f000, # 011111100001101011101111100011100001011111000000000000
				7: 0x7e1aef8e17c0    # 000000011111100001101011101111100011100001011111000000
			}
		},
		# 台历2菜单图标
		MENU_CALENDAR_2: {
			'period': 40,
			'loops' : False,
			'frames': {
				0: 0x1f000000000000, # 011111000000000000000000000000000000000000000000000000
				1: 0x217c0000000000, # 100001011111000000000000000000000000000000000000000000
				2: 0x2385f000000000, # 100011100001011111000000000000000000000000000000000000
				3: 0x2f8e17c0000000, # 101111100011100001011111000000000000000000000000000000
				4: 0x29be385f000000, # 101001101111100011100001011111000000000000000000000000
				5: 0x21a6f8e17c0000, # 100001101001101111100011100001011111000000000000000000
				6: 0x1f869be385f000, # 011111100001101001101111100011100001011111000000000000
				7: 0x7e1a6f8e17c0    # 000000011111100001101001101111100011100001011111000000
			}
		},
		# 在线更新菜单图标
		MENU_UPDATE: {
			'period': 40,
			'loops' : False,
			'frames': {
				0: 0x8000000000000,  # 001000000000000000000000000000000000000000000000000000
				1: 0x10200000000000, # 010000001000000000000000000000000000000000000000000000
				2: 0x2f408000000000, # 101111010000001000000000000000000000000000000000000000
				3: 0x10bd0200000000, # 010000101111010000001000000000000000000000000000000000
				4: 0x842f408000000,  # 001000010000101111010000001000000000000000000000000000
				5: 0x210bd0200000,   # 000000001000010000101111010000001000000000000000000000
				6: 0x842f408000,     # 000000000000001000010000101111010000001000000000000000
			}
		}
	}

	def __init__(self):
		self.__period = Animation.DEFAULT_PERIOD
		self.__loops  = Animation.DEFAULT_LOOPS
		self.__steps  = Animation.DEFAULT_STEPS
		self.__frames = None
		self.__colors = None

		self.__frames_gen = None
		self.__colors_gen = None

	def select_animation(self, animation:int, colors:tuple):
		'''选择一个动画效果'''
		if animation not in Animation.ANIMATION_LIST:
			raise AnimationException('invalid animation')

		resource = Animation.RESOURCES[animation]
		frames = resource.get('frames')

		if frames and len(frames) > 0:
			self.__frames = frames
			self.__frames_gen = self.__frame_generator()
		else:
			raise AnimationException('invalid frames')

		if isinstance(colors, (tuple, list)) and len(colors) > 0:
			self.__colors = colors
			self.__colors_gen = self.__color_generator()
		else:
			raise AnimationException('invalid colors')

		self.__period = resource.get('period', Animation.DEFAULT_PERIOD)
		self.__loops  = resource.get('loops', Animation.DEFAULT_LOOPS)
		self.__steps  = resource.get('steps', Animation.DEFAULT_STEPS)

	def get_frame_and_color(self) -> tuple:
		'''
		获取当前帧数据和颜色

		@return: 剩余帧数, 当前帧数据, 当前颜色数据
		'''
		remains, frame = next(self.__frames_gen)
		return remains, frame, next(self.__colors_gen)

	def __frame_generator(self) -> tuple:
		'''帧数据生成器'''
		index = 0
		count = len(self.__frames)

		while True:
			yield count - index - 1, self.__frames[index]
			index = (index + 1) % count

	def __color_generator(self) -> tuple:
		'''颜色数据生成器'''
		while True:
			if isinstance(self.colors[0], int):
				yield self.colors
			elif isinstance(self.colors[0], tuple):
				if len(self.colors) == 1:
					yield self.colors[0]
				else:
					for index, color in enumerate(self.colors):
						next_index = (index + 1) % len(self.colors)
						next_color = self.colors[next_index]

						for step in range(1, self.steps + 1):
							r = int(color[0] + (next_color[0] - color[0]) * step / self.steps)
							g = int(color[1] + (next_color[1] - color[1]) * step / self.steps)
							b = int(color[2] + (next_color[2] - color[2]) * step / self.steps)

							yield (r, g, b)


	#region class properties
	@property
	def steps(self):
		return self.__steps

	@steps.setter
	def steps(self, value:int):
		'''设置/获取颜色分段数量'''
		self.__steps = value

	@property
	def period(self):
		return self.__period

	@period.setter
	def period(self, value:int):
		'''设置/获取显示间隔时长'''
		self.__period = value

	@property
	def loops(self):
		return self.__loops

	@loops.setter
	def loops(self, value:bool):
		'''设置/获取是否循环播放'''
		self.__loops = value

	@property
	def colors(self):
		return self.__colors

	@colors.setter
	def colors(self, value:tuple(tuple, list)):
		'''设置/获取要显示的颜色'''
		if isinstance(value, (tuple, list)) and len(value) > 0:
			self.__colors = value
			self.__colors_gen = self.__color_generator(value)
	#endregion


if __name__ == '__main__':
	from utils.dispatcher import Dispatcher
	from matrix.ws2812 import WS2812
	from utils.utilities import Utilities


	CONFIG = Utilities.import_config()
	current_animation = 0

	def zfill_54bin(value:int):
		return f'{value:054b}'

	def show_animation():
		remains, frame, color = animation.get_frame_and_color()

		for index, bit in enumerate(zfill_54bin(frame)):
			ws2812.__neopixel[index] = color if bit == '1' else CONFIG.COLORS.BLACK

		ws2812.show()

		if not animation.loops and remains == 0:
			tasks.del_work(show_animation)

	def show_test():
		animation.select_animation(
			Animation.SUCCESS,
			(
				# ws2812.convert_color(CONFIG.COLORS.BLACK),
				# ws2812.convert_color(CONFIG.COLORS.LIGHTGREEN),
				ws2812.convert_color((0, 128, 0))
			)
		)

		tasks.add_work(show_animation, animation.period)

	def show_tests():
		global current_animation
		colors = None

		if current_animation == Animation.CONFIG_WIFI:
			colors = (
				ws2812.convert_color((255, 0, 0)),
				ws2812.convert_color((0, 255, 0)),
				ws2812.convert_color((0, 0, 255))
			)
		elif current_animation == Animation.CONNECT_WIFI:
			colors = ws2812.convert_color((0, 255, 0))
		elif current_animation == Animation.HEARTBEAT:
			colors = ws2812.convert_color((255, 0, 0))
		elif current_animation == Animation.MENU_CLOCK:
			colors = ws2812.convert_color((128, 128, 128))
		elif current_animation == Animation.MENU_CALENDAR_1:
			colors = ws2812.convert_color((128, 0, 128))
		elif current_animation == Animation.MENU_CALENDAR_2:
			colors = ws2812.convert_color((0, 128, 128))
		elif current_animation == Animation.MENU_UPDATE:
			colors = ws2812.convert_color((0, 128, 128))
		elif current_animation == Animation.UPDATING:
			colors = ws2812.convert_color((128, 128, 128))
		elif current_animation == Animation.SUCCESS:
			colors = ws2812.convert_color((0, 128, 0))
		elif current_animation == Animation.FAILED:
			colors = ws2812.convert_color((128, 0, 0))

		animation.select_animation(current_animation, colors)
		tasks.add_work(show_animation, animation.period)
		tasks.add_work(show_tests, 8000)

		current_animation = (current_animation + 1) % len(Animation.ANIMATION_LIST)


	ws2812    = WS2812(CONFIG.WS2812_MATRIX.WIDTH, CONFIG.WS2812_MATRIX.HEIGHT, CONFIG.PINS.DIN_MATRIX)
	tasks     = Dispatcher()
	animation = Animation()

	ws2812.brightness = 40

	# show_test()
	show_tests()
