"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
if __name__ == '__main__':
	try:
		Runner = __import__('./runner').Runner
	except ImportError:
		from runner import Runner

	runner = Runner()
	runner.start()
