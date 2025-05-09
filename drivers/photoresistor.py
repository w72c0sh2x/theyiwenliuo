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

	LEVELS_RANGE = {
		LEVEL_1: [0, 300],
		LEVEL_2: [301, 800],
		LEVEL_3: [801, 2000],
		LEVEL_4: [2001, 3000],
		LEVEL_5: [3001, 4095],
	}

	def __init__(self, pin:int):
		self.__adc = ADC(Pin(pin))
		self.__adc.atten(ADC.ATTN_11DB)

	@property
	def level(self):
		samples = []

		for _ in range(3):
			samples.append(self.__adc.read())
			sleep(0.1)
		
		sample_avg = int((samples[0] + samples[1] + samples[2]) / 3)

		for level, level_range in Photoresistor.LEVELS_RANGE.items():
			if level_range[0] <= sample_avg <= level_range[1]:
				return level

		return False


if __name__ == '__main__':
	adc = Photoresistor(Config.PINS.ADC)

	for _ in range(10):
		print(f'adc level: {adc.level}')
		sleep(1)
