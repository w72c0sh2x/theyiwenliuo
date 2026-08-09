"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
class Utilities(object):
	STA_CONFIG_FILENAME = 'sta_config.py'

	@staticmethod
	def import_config():
		try:
			Config = __import__('./config').Config
		except ImportError:
			from config import Config

		return Config

	@staticmethod
	def is_esp32c3():
		from machine import Pin
		from os import uname

		if uname()[0] == 'esp32':
			try:
				Pin(22, Pin.OUT)
				return False
			except ValueError:
				return True

	@staticmethod
	def soft_reset():
		from sys import exit
		exit()

	@staticmethod
	def hard_reset():
		from machine import reset
		reset()

	@staticmethod
	def output_sta_config_file(essid, password):
		with open(Utilities.STA_CONFIG_FILENAME, 'w') as output:
			output.write(
f'''# automatic generated file
essid = '{essid}'
password = '{password}'
'''
			)

	@staticmethod
	def delete_sta_config_file():
		import os
		try:
			os.remove(Utilities.STA_CONFIG_FILENAME)
		except:
			pass
