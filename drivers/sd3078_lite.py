"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from micropython import const
from machine import SoftI2C, I2C, Pin, RTC


LOCALTIME_YEAR    = 0
LOCALTIME_MONTH   = 1
LOCALTIME_DAY     = 2
LOCALTIME_HOUR    = 3
LOCALTIME_MINUTE  = 4
LOCALTIME_SECOND  = 5
LOCALTIME_WEEKDAY = 6
LOCALTIME_YEARDAY = 7


#region registers
REG_RTC_SECOND  = const(0x00)
REG_RTC_MINUTE  = const(0x01)
REG_RTC_HOUR    = const(0x02)
REG_RTC_WEEKDAY = const(0x03)
REG_RTC_DAY     = const(0x04)
REG_RTC_MONTH   = const(0x05)
REG_RTC_YEAR    = const(0x06)

REG_CTRL_CTR1   = const(0x0f)
REG_CTRL_CTR2   = const(0x10)

# 寄存器控制位
BIT_WRTC1 = 1 << 7 # REG_CTRL_CTR2
BIT_WRTC2 = 1 << 2 # REG_CTRL_CTR1
BIT_WRTC3 = 1 << 7 # REG_CTRL_CTR1
#endregion


class SD3078EXCEPTION(BaseException):
	pass


# https://www.whwave.com.cn/SD3078
class SD3078Lite(object):
	IIC_ADDR = 0x32 # 011 0010

	def __init__(self, i2c:SoftI2C=None):
		assert isinstance(i2c, (SoftI2C, I2C)), SD3078EXCEPTION('i2c is not I2C instance')
		self.__i2c = i2c

	def datetime(self, dt=None):
		'''设置/获取芯片中的日期时间，日期格式与 localtime() 相同'''
		# utime.localtime()
		# (year, month, mday, hour, minute, second, weekday, yearday)
		if dt is not None:
			if len(dt) == 8:
				data = []
				data.append(self.__dec2bcd(dt[LOCALTIME_SECOND]))
				data.append(self.__dec2bcd(dt[LOCALTIME_MINUTE]))
				data.append(self.__dec2bcd(dt[LOCALTIME_HOUR]) | 0x80)
				data.append(self.__dec2bcd((dt[LOCALTIME_WEEKDAY] + 1) % 7))
				data.append(self.__dec2bcd(dt[LOCALTIME_DAY]))
				data.append(self.__dec2bcd(dt[LOCALTIME_MONTH]))
				data.append(self.__dec2bcd(dt[LOCALTIME_YEAR] - 2000))

				self.__write_enabled(True)
				self.__write_mem(REG_RTC_SECOND, data)
				self.__write_enabled(False)
		else:
			result = []
			data = self.__read_mem(REG_RTC_SECOND, 7)

			result.append( self.__bcd2dec(data[REG_RTC_YEAR]    & 0x7f) + 2000)
			result.append( self.__bcd2dec(data[REG_RTC_MONTH]   & 0x1f))
			result.append( self.__bcd2dec(data[REG_RTC_DAY]     & 0x3f))
			result.append( self.__bcd2dec(data[REG_RTC_HOUR]    & 0x3f))
			result.append( self.__bcd2dec(data[REG_RTC_MINUTE]  & 0x7f))
			result.append( self.__bcd2dec(data[REG_RTC_SECOND]  & 0x7f))
			result.append((self.__bcd2dec(data[REG_RTC_WEEKDAY] & 0x07) - 1) % 7)

			RTC().datetime((
				result[LOCALTIME_YEAR],
				result[LOCALTIME_MONTH],
				result[LOCALTIME_DAY],
				result[LOCALTIME_WEEKDAY],
				result[LOCALTIME_HOUR],
				result[LOCALTIME_MINUTE],
				result[LOCALTIME_SECOND], 0
			))


	#region class properties
	@property
	def power_lost(self):
		'''
		获取芯片供电状态，用于判断芯片是否经过校时
		- 掉电后再次上电返回 True
		- 上电后写入数据返回 False
		'''
		return self.__read_mem(REG_CTRL_CTR1)[0] & 0x01
	#endregion


	#region tools function
	def __write_mem(self, mem_addr:int, data):
		'''向指定的寄存器写入数据'''
		if isinstance(data, int):
			data = [data]

		self.__i2c.writeto_mem(SD3078Lite.IIC_ADDR, mem_addr, bytearray(data))

	def __read_mem(self, mem_addr:int, nbytes=1):
		'''从指定的寄存器读取数据'''
		return bytearray(self.__i2c.readfrom_mem(SD3078Lite.IIC_ADDR, mem_addr, nbytes))

	def __write_enabled(self, enabled:bool):
		'''启用/禁用数据写入功能'''
		data = self.__read_mem(REG_CTRL_CTR1, 2)

		if enabled:
			data[1] |= BIT_WRTC1
			self.__write_mem(REG_CTRL_CTR2, data[1])

			data[0] |= BIT_WRTC2
			data[0] |= BIT_WRTC3
			self.__write_mem(REG_CTRL_CTR1, data[0])
		else:
			data[0] &= ~BIT_WRTC2
			data[0] &= ~BIT_WRTC3
			data[1] &= ~BIT_WRTC1
			self.__write_mem(REG_CTRL_CTR1, data[0])

	def __dec2bcd(self, dec:int):
		'''十进制数转 BCD 码，范围：0~99'''
		if not dec in range(0, 99):
			return 0

		return ((dec // 10) << 4) + (dec % 10)

	def __bcd2dec(self, bcd:int):
		'''BCD 码转十进制数，范围：0x00~0x99'''
		if not bcd in range(0x00, 0x99):
			return 0

		return (bcd >> 4) * 10 + (bcd & 0x0f)
	#endregion


if __name__ == '__main__':
	import utime

	i2c = SoftI2C(scl=Pin(18), sda=Pin(19))
	sd3078 = SD3078Lite(i2c)

	# utime.localtime()
	# (year, month, mday, hour, minute, second, weekday, yearday)
	datetime = (2023, 6, 30, 12, 17, 40, 4, 0)

	if sd3078.power_lost:
		sd3078.datetime(datetime)

	sd3078.datetime()
	print(f'localtime: {utime.localtime()}')
