"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
__version__ = '0.1'
__version_info__ = (0, 1)
print('module animation version:', __version__)


class AnimationException(Exception):
	pass


class Animation(object):
	'''生成简易动画数据'''
	CONFIG_WIFI  = 0
	CONNECT_WIFI = 1
	HEARTBEAT    = 2

	ANIMATION_LIST = [
		CONFIG_WIFI,
		CONNECT_WIFI,
		HEARTBEAT
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
			'period': 150,
			'frames': {
				0: 0x850a508000,   # 000000000000001000010100001010010100001000000000000000
				1: 0xc48948c000,   # 000000000000001100010010001001010010001100000000000000
				2: 0x8522448462508 # 001000010100100010010001001000010001100010010100001000
			}
		}
	}

	def __init__(self):
		self.__period = 50
		self.__steps  = 10
		self.__frames = None
		self.__colors = None

		self.__frames_gen = None
		self.__colors_gen = None

	def select_animation(self, animation, colors:tuple):
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

		self.__period = resource.get('period', self.__period)
		self.__steps  = resource.get('steps', self.__steps)

	def get_frame_and_color(self):
		'''获取当前帧数据和颜色'''
		return next(self.__frames_gen), next(self.__colors_gen)

	def __frame_generator(self):
		'''帧数据生成器'''
		index = 0
		count = len(self.__frames)

		while True:
			yield self.__frames[index]
			index = (index + 1) % count

	def __color_generator(self):
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
	colors = None
	current_animation = 0

	def zfill_54bin(value):
		return f'{value:054b}'

	def show_animation():
		frame, color = animation.get_frame_and_color()

		for index, bit in enumerate(zfill_54bin(frame)):
			ws2812.__neopixel[index] = color if bit == '1' else CONFIG.COLORS.BLACK

		ws2812.show()

	def show_test():
		animation.select_animation(
			Animation.CONFIG_WIFI,
			(
				ws2812.convert_color(CONFIG.COLORS.BLACK),
				ws2812.convert_color(CONFIG.COLORS.LIGHTGREEN),
				ws2812.convert_color(CONFIG.COLORS.SKYBLUE)
			)
		)

		tasks.add_work(show_animation, animation.period)

	def show_tests():
		global current_animation, colors

		if current_animation == 0:
			colors = (
				ws2812.convert_color((255, 0, 0)),
				ws2812.convert_color((0, 255, 0)),
				ws2812.convert_color((0, 0, 255))
			)
		elif current_animation == 1:
			colors = ws2812.convert_color((0, 255, 0))
		elif current_animation == 2:
			colors = ws2812.convert_color((255, 0, 0))

		animation.select_animation(current_animation, colors)
		tasks.add_work(show_animation, animation.period)
		tasks.add_work(show_tests, 8000)

		current_animation = (current_animation + 1) % len(Animation.ANIMATION_LIST)


	ws2812    = WS2812(CONFIG.WS2812_MATRIX.WIDTH, CONFIG.WS2812_MATRIX.HEIGHT, CONFIG.PINS.DIN_MATRIX)
	tasks     = Dispatcher()
	animation = Animation()

	ws2812.brightness = 40

	# show_test1()
	show_tests()
