"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
__version__ = '0.1.1'
__version_info__ = (0, 1, 1)
print('module runner version:', __version__)

import os
import gc
import mip
import network
from machine import reset


UPDATE_PATH = '/update'
UPDATE_CONFIG_FILE = 'ota_config.py'
URL_PREFIX = 'https://gitee.com/walkline/micropython-ws2812-led-clock/raw/master'
# URL_PREFIX = 'https://walkline.wang'
UPDATE_CONFIG_URL = f'{URL_PREFIX}{UPDATE_PATH}/{UPDATE_CONFIG_FILE}'
IMPORT_CONFIG_FILE = f'{UPDATE_PATH}/{UPDATE_CONFIG_FILE.replace(".py", "")}'


class FileUtilities(object):
	'''
	文件操作类模块
	'''
	def mkdirs(self, dirs:str):
		last_dir = ''

		for dir in dirs.split('/'):
			if len(dir) == 0:
				continue

			try:
				os.mkdir(f'{last_dir}/{dir}')
			except:
				pass

			last_dir += f'/{dir}'

	def move(self, src, dest):
		with open(src, 'rb') as src_file:
			with open(dest, 'wb') as dest_file:
				dest_file.write(src_file.read())
				dest_file.flush()

		self.remove(src)

	def remove(self, file):
		try:
			os.remove(file)
		except OSError:
			pass

	def exist(self, file):
		try:
			os.stat(file)
			return True
		except OSError:
			return False


class OnlineUpdater(FileUtilities):
	def __init__(self):
		self.mkdirs(UPDATE_PATH)

	def check(self):
		if not network.WLAN(network.STA_IF).isconnected():
			print('no internet connection, update terminated!')
			return

		need_hard_reset = False
		update_files = self.__get_update_config()

		for file in update_files.values():
			full_path = f'{file["path"]}/{file["filename"]}'.replace('//', '/')
			version_info = self.__get_file_version_info(full_path)

			print(f'[{full_path}] remote update version: {file["version"]}')

			if version_info is None or file['version'] > version_info:
				mip.install(file['url'], target=UPDATE_PATH)
				self.mkdirs(file['path'])

				temp_filename = f'{UPDATE_PATH}/{file["filename"]}'.replace('//', '/')

				if self.exist(temp_filename):
					if os.stat(temp_filename)[6] == file['size']:
						self.move(temp_filename, full_path)
						need_hard_reset = True

						print(f'[{full_path}] up to date from {version_info} to {file["version"]}')
					else:
						print(f'[{temp_filename}] download incompleted!')
				else:
					print(f'[{temp_filename}] download failed!')
			else:
				print(f'[{full_path}] already up to date!')

		gc.collect()

		if need_hard_reset:
			print('update completed, hard reset now...')
			network.WLAN(network.STA_IF).active(False)
			reset()

	def __get_update_config(self) -> dict:
		'''
		从在线更新配置文件获取要更新的文件信息
		'''
		result = {}

		self.remove(f'{UPDATE_PATH}/{UPDATE_CONFIG_FILE}')
		mip.install(UPDATE_CONFIG_URL, target=UPDATE_PATH)

		if self.exist(f'{IMPORT_CONFIG_FILE}.py'):
			import_file = __import__(IMPORT_CONFIG_FILE)

			if hasattr(import_file, 'files'):
				result = import_file.files

		return result

	def __get_file_version_info(self, filename:str):
		'''
		获取本地文件版本信息
		'''
		result = None

		if self.exist(filename):
			import_file = __import__(f'.{filename.replace(".mpy", "")}')

			if hasattr(import_file, '__version_info__'):
				result = import_file.__version_info__
				print(f'[{filename}] local existed, version: {result}')
			else:
				print(f'[{filename}] local existed, has no version info')
		else:
			try:
				import_file = __import__(f'.frozen/{filename.replace(".mpy", "")}'.replace('//', '/'))

				if hasattr(import_file, '__version_info__'):
					result = import_file.__version_info__
					print(f'[{filename}] not exist, frozen file version: {result}')
				else:
					print(f'[{filename}] not exist, frozen file has no version info')
			except ImportError:
				print(f'[{filename}] not exist in file system')

		return result


if __name__ == '__main__':
	from utils.wifihandler import WifiHandler

	if WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode(timeout_sec=120):
		OnlineUpdater().check()
