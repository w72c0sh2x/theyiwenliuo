"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
__version__ = '0.1.2'
__version_info__ = (0, 1, 2)
print('module update version:', __version__)


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
	ERROR_UPDATE_SUCCESS   = 0
	ERROR_UPDATE_FAILED    = 1
	ERROR_NO_INTERNET      = 2
	ERROR_NO_CONFIG_FILE   = 3
	ERROR_DOWNLOAD_SUCCESS = 4
	ERROR_DOWNLOAD_FAILED  = 5
	ERROR_DOWNLOAD_INCOMPLETED = 5

	def __init__(self, result_cb:function=None):
		# result_cb(result:int, msg:str, files:dict)
		# files
		# {
		# 	{
		# 		'xxx.py': {
		# 		'path'         : '/utils',
		# 		'size'         : 2459,
		# 		'local_version': None,
		# 		'filename'     : 'xxx.mpy',
		# 		'full_path'    : '/utils/xxx.mpy'
		# 		'result'       : 4,
		# 		'version'      : (0, 1, 1)
		# 	},
		# }
		self.__result_cb = result_cb

		if not callable(result_cb):
			self.__result_cb = None

		self.mkdirs(UPDATE_PATH)

	def check(self, retry:int=3):
		'''
		检查服务器更新文件并自动完成更新
		'''
		if not network.WLAN(network.STA_IF).isconnected():
			print('no internet connection, update terminated!')

			if self.__result_cb is not None:
				self.__result_cb(OnlineUpdater.ERROR_NO_INTERNET, 'no internet connection', None)
			return

		# 可更新的文件列表
		update_file_list = self.__get_update_config()

		if len(update_file_list) == 0:
			if self.__result_cb is not None:
				self.__result_cb(OnlineUpdater.ERROR_NO_CONFIG_FILE, 'no update config file exists', None)
			return

		# 需要更新的文件列表
		updating_file_list = self.__analyse_update_files(update_file_list)
		del update_file_list

		if len(updating_file_list) == 0:
			if self.__result_cb is not None:
				self.__result_cb(OnlineUpdater.ERROR_UPDATE_SUCCESS, 'already up to date', None)
			return

		downloading_file_list = self.__download_updating_files(updating_file_list, retry)

		update_success = True
		for file in downloading_file_list.values():
			if file['result'] != OnlineUpdater.ERROR_DOWNLOAD_SUCCESS:
				update_success = False
				break

		if update_success:
			for file in downloading_file_list.values():
				self.move(file['temp_file'], file['full_path'])
				file.pop('url')
				file.pop('temp_file')

			if self.__result_cb is not None:
				self.__result_cb(OnlineUpdater.ERROR_UPDATE_SUCCESS, 'update success', downloading_file_list)
		else:
			for file in downloading_file_list.values():
				file.pop('url')
				file.pop('temp_file')

			if self.__result_cb is not None:
				self.__result_cb(OnlineUpdater.ERROR_UPDATE_FAILED, 'update failed', downloading_file_list)			

		del downloading_file_list
		gc.collect()

	def __get_update_config(self) -> dict:
		'''
		从在线更新配置文件获取可以更新的文件列表
		'''
		result = {}

		self.remove(f'{UPDATE_PATH}/{UPDATE_CONFIG_FILE}')
		mip.install(UPDATE_CONFIG_URL, target=UPDATE_PATH)

		if self.exist(f'{IMPORT_CONFIG_FILE}.py'):
			import_file = __import__(IMPORT_CONFIG_FILE)

			if hasattr(import_file, 'files'):
				result = import_file.files

		return result

	def __analyse_update_files(self, files:dict) -> dict:
		'''
		分析可更新文件列表，获取需要的文件信息
		'''
		result = {}

		for key, file in files.items():
			full_path = f'{file["path"]}/{file["filename"]}'.replace('//', '/')
			version = self.__get_file_version_info(full_path)

			if version is None or file['version'] > version:
				file['full_path'] = full_path
				file['local_version'] = version
				result[key] = file

		return result

	def __download_updating_files(self, files:dict, retry:int) -> dict:
		'''
		下载需要更新的文件
		'''
		result = {}

		for key, file in files.items():
			for count in range(1, retry + 1):
				print(f'- try to download file {file["filename"]} ({count}/{retry})')
				mip.install(file['url'], target=f'{UPDATE_PATH}{file["path"]}')

				temp_file = f'{UPDATE_PATH}{file["path"]}/{file["filename"]}'.replace('//', '/')

				if self.exist(temp_file):
					if os.stat(temp_file)[6] == file['size']:
						file['result']    = OnlineUpdater.ERROR_DOWNLOAD_SUCCESS
						file['message']   = 'download success'
						file['temp_file'] = temp_file

						result[key] = file
						break
					else:
						file['result']  = OnlineUpdater.ERROR_DOWNLOAD_INCOMPLETED
						file['message'] = 'download incompleted'
						print(f'[{temp_file}] download incompleted!')
				else:
					file['result']  = OnlineUpdater.ERROR_DOWNLOAD_FAILED
					file['message'] = 'download failed'
					print(f'[{temp_file}] download failed!')

				result[key] = file

		return result

	def __get_file_version_info(self, filename:str) -> tuple:
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

	def update_callback(result:int, msg:str, files:dict):
		print(f'- result: {msg}')

		if files:
			for file in files.values():
				if file['result'] == OnlineUpdater.ERROR_DOWNLOAD_SUCCESS:
					print(f'    [{file["full_path"]}] up to date from {file["local_version"]} to {file["version"]}')
				elif file['result'] in (OnlineUpdater.ERROR_DOWNLOAD_INCOMPLETED, OnlineUpdater.ERROR_DOWNLOAD_FAILED):
					print(f'    [{file["full_path"]}] {file["message"]}')

		if result == OnlineUpdater.ERROR_UPDATE_SUCCESS and files:
			print('update completed, hard reset now...')
			# network.WLAN(network.STA_IF).active(False)
			# reset()

	if not network.WLAN(network.STA_IF).isconnected():
		WifiHandler.STATION_CONNECTED == WifiHandler.set_sta_mode(timeout_sec=120)

	updater = OnlineUpdater(update_callback)
	updater.check()
