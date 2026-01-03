"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
class Animation(object):
	'''
	生成简易动画数据，目前仅支持白色
	'''
	EFFECT_NORMAL = 0
	EFFECT_FADE_IN = 1
	EFFECT_FADE_OUT = 2
	EFFECT_FADE_IN_AND_OUT = 3

	__EFFECTS = {
		EFFECT_NORMAL,
		EFFECT_FADE_IN,
		EFFECT_FADE_OUT,
		EFFECT_FADE_IN_AND_OUT
	}

	ANIMATION_CONNECTING_1 = 0
	__ANIMATION_CONNECTING_1_FRAMES = {
		0: '000000000010000000000110000000001110000000011110000000' # 0x80180380780
	}

	ANIMATION_CONNECTING_2 = 1
	__ANIMATION_CONNECTING_2_FRAMES = {
		0: '000000000010000000000000000000000000000000000000000000',
		1: '000000000010000000000110000000000000000000000000000000',
		2: '000000000010000000000110000000001110000000000000000000',
		3: '000000000010000000000110000000001110000000011110000000'
	}

	ANIMATION_HEARTBEAT = 2
	__ANIMATION_HEARTBEAT_FRAMES = {
		0: '000000000000001000010100001010010100001000000000000000',
		1: '000000000000001100010010001001010010001100000000000000',
		2: '001000010100100010010001001000010001100010010100001000'
	}

	__ANIMATIONS = {
		# 呼吸效果的连接指示动画
		ANIMATION_CONNECTING_1: {
			'effect': EFFECT_FADE_IN_AND_OUT,
			'frames': __ANIMATION_CONNECTING_1_FRAMES
		},
		# 动态增加效果的连接指示动画
		ANIMATION_CONNECTING_2: {
			'effect': EFFECT_NORMAL,
			'frames': __ANIMATION_CONNECTING_2_FRAMES
		},
		# 心跳动画
		ANIMATION_HEARTBEAT: {
			'effect': EFFECT_NORMAL,
			'frames': __ANIMATION_HEARTBEAT_FRAMES
		}
	}

	__COLOR_MIN = 0
	__COLOR_MAX = 200

	def __init__(self):
		self.__effect = self.EFFECT_NORMAL
		self.__color_step = 20
		self.__frames = None
		self.__colors = None

	def __set_effect(self, effect):
		if effect in self.__EFFECTS:
			self.__effect = effect
		else:
			print('invalid effect')

	def select_animation(self, animation):
		'''
		选择一个当前显示的动画效果
		'''
		if animation in self.__ANIMATIONS:
			self.__effect = self.__ANIMATIONS[animation]['effect']
			self.__frames = self.__frame_generator(self.__ANIMATIONS[animation]['frames'])
			self.__colors = self.__color_generator()
		else:
			print('invalid animation')

	def get_frame_and_color(self):
		'''
		获取当前帧数据和颜色
		'''
		return next(self.__frames), next(self.__colors)

	def set_color_step(self, step):
		'''
		设置颜色递增/递减步长
		'''
		self.__color_step = abs(step)

	def __frame_generator(self, frames):
		'''
		帧数据生成器
		'''
		index = 0
		count = len(frames)

		while True:
			yield frames[index]

			index += 1

			if index >= count: index = 0

	def __color_generator(self):
		'''
		颜色数据生成器
		'''
		color = self.__COLOR_MIN
		step = abs(self.__color_step)

		if self.__effect in (self.EFFECT_FADE_OUT, self.EFFECT_NORMAL):
			color = self.__COLOR_MAX

		while True:
			yield color

			if self.__effect == self.EFFECT_FADE_IN:
				color += step

				if color >= self.__COLOR_MAX:
					color = self.__COLOR_MIN
			elif self.__effect == self.EFFECT_FADE_OUT:
				color -= step

				if color <= self.__COLOR_MIN:
					color = self.__COLOR_MAX
			elif self.__effect == self.EFFECT_FADE_IN_AND_OUT:
				color += step

				if color >= self.__COLOR_MAX or color <= self.__COLOR_MIN:
					step = -step


if __name__ == '__main__':
	from utils.dispatcher import Dispatcher

	def show_animation():
		frame, color = animate.get_frame_and_color()

		print(f'\ncolor: {color}')

		for row in range(6):
			for col in range(9):
				index = col * 6 + row
				print('{}'.format(frame[index].replace('0', '.').replace('1', '@')), end='')
			print('')
		print('')

	tasks = Dispatcher()
	animate = Animation()

	animate.select_animation(Animation.ANIMATION_HEARTBEAT)
	animate.set_color_step(20)

	tasks.add_work(show_animation, 1000 * 3)
