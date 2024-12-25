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
from utime import sleep
import network
import smartconfig

station = network.WLAN(network.STA_IF)
station.active(True)

smartconfig.start()

while not smartconfig.success():
	sleep(0.5)

print(smartconfig.info())

>>> ('ssid', 'password')
'''
