#!/usr/bin/env python3
# coding=utf-8
"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-mini-calendar
"""
import os
import subprocess


# pip install mpy-cross
MPY_CROSS = 'mpy-cross'

OUTPUT_PATH = 'update'
OUTPUT_FILE = 'ota_config.py'
INPUT_FILE_LIST = (
	'/config.py',
	'/runner.py',
	'/matrix/animation.py',
	'/matrix/matrix_clock.py',
	'/utils/update.py',
	'/utils/ble_config.py'
)
URL_PREFIX = 'https://gitee.com/walkline/micropython-ws2812-led-clock/raw/master'


def preview(output:dict):
	for idnex, file_info in output.items():
		print(
f'''[{idnex}]:
        path: '{file_info['path']}'
    filename: '{file_info['filename']}'
        size: {file_info['size']}
         url: '{file_info['url']}'
     version: {file_info['version']}
''')


if __name__ == '__main__':
	output = {}

	for file in INPUT_FILE_LIST:
		file_info = {}
		input_file = file[1:]

		if not os.path.exists(input_file):
			continue

		file_info['path'], filename = os.path.split(file)
		file_info['filename'] = f'{os.path.splitext(filename)[0]}.mpy'
		output_file = f'{OUTPUT_PATH}/{file_info["filename"]}'

		result = subprocess.run(f'{MPY_CROSS} {input_file} -o {output_file}', shell=True)

		if result.returncode != 0:
			continue

		file_info['size'] = os.stat(output_file)[6]
		file_info['url'] = f'{URL_PREFIX}/{output_file}'

		with open(input_file, encoding='utf-8') as lines:
			for line in lines:
				if line.strip().startswith('__version_info__'):
					file_info['version'] = eval(line.strip().split('=')[1])
					break

		if file_info.get('version'):
			output[filename] = file_info

	preview(output)

	if len(output) > 0:
		with open(f'{OUTPUT_PATH}\{OUTPUT_FILE}', 'w', encoding='utf-8') as output_file:
			output_file.write(
f'''# automatic generated file
files = {output}
''')
