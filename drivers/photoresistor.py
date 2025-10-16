"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-research
"""
from config import Config
from machine import Pin, ADC
from utime import sleep


class Photoresistor(object):
	'''
	光敏电阻驱动
	'''
	LEVEL_1 = 1 # 亮度最大
	LEVEL_2 = 2
	LEVEL_3 = 3
	LEVEL_4 = 4
	LEVEL_5 = 5
	LEVEL_6 = 6

	LEVELS_RANGE = {
		LEVEL_1: [0, 450],
		LEVEL_2: [451, 900],
		LEVEL_3: [901, 1300],
		LEVEL_4: [1301, 1900],
		LEVEL_5: [1901, 3000],
		LEVEL_6: [3001, 4095]
	}

	def __init__(self, pin:int):
		self.__adc = ADC(Pin(pin))
		self.__adc.atten(ADC.ATTN_11DB)

	@property
	def level(self):
		sample_avg = 0

		for _ in range(20):
			sample_avg += self.__adc.read()
			# sleep(0.05)

		sample_avg = int(sample_avg / 20)

		for level, level_range in Photoresistor.LEVELS_RANGE.items():
			if level_range[0] <= sample_avg <= level_range[1]:
				return level

		return Photoresistor.LEVEL_6


if __name__ == '__main__':
	adc = Photoresistor(Config.PINS.ADC)

	for _ in range(10000):
		print(f'adc level: {adc.level}')
		sleep(0.2)
