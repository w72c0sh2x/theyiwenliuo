"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
if __name__ == '__main__':
	try:
		from runner import Runner
	except ImportError:
		Runner = __import__('runner').Runner

	runner = Runner()
	runner.start()
