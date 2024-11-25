"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
def start() -> None:
	...

def success() -> bool:
	...

def info() -> tuple:
	...


'''
import smartconfig

smartconfig.start()

while not smartconfig.success():
	sleep(0.5)

print(smartconfig.info())

>>> ('ssid', 'password')
'''
