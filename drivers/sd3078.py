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

# REG_ALARM_SECOND  = const(0x07)
# REG_ALARM_MINUTE  = const(0x08)
# REG_ALARM_HOUR    = const(0x09)
# REG_ALARM_WEEKDAY = const(0x0a)
# REG_ALARM_DAY     = const(0x0b)
# REG_ALARM_MONTH   = const(0x0c)
# REG_ALARM_YEAR    = const(0x0d)
# REG_ALARM_ENABLE  = const(0x0e)

REG_CTRL_CTR1   = const(0x0f)
REG_CTRL_CTR2   = const(0x10)
# REG_CTRL_CTR3   = const(0x11)
# REG_CTRL_CTR4   = const(0x19)
REG_CTRL_CTR5   = const(0x1a)
# REG_CTRL_25_TTF = const(0x12)
# REG_COUNTDOWN   = const(0x13)

REG_TEMP       = const(0x16)
# REG_TEMP_AL    = const(0x1c)
# REG_TEMP_AH    = const(0x1d)
REG_TEMP_HIS_L = const(0x1e)
REG_TEMP_HIS_H = const(0x1f)

REG_IIC_CTRL   = const(0x17)
REG_BAT_CHARGE = const(0x18)
REG_BAT_VAL    = const(0x1b)

REG_HIS_L_MINUTE  = const(0x20)
# REG_HIS_L_HOUR    = const(0x21)
# REG_HIS_L_WEEKDAY = const(0x22)
# REG_HIS_L_DAY     = const(0x23)
# REG_HIS_L_MONTH   = const(0x24)
# REG_HIS_L_YEAR    = const(0x25)

REG_HIS_H_MINUTE  = const(0x26)
# REG_HIS_H_HOUR    = const(0x27)
# REG_HIS_H_WEEKDAY = const(0x28)
# REG_HIS_H_DAY     = const(0x29)
# REG_HIS_H_MONTH   = const(0x2a)
# REG_HIS_H_YEAR    = const(0x2b)

REG_USER_RAM_START = const(0x2c) # 0x2c to 0x71 (70 bytes)
REG_USER_RAM_END   = const(0x71)
REG_CHIP_ID        = const(0x72) # 0x72 to 0x79 (8 bytes)

# 寄存器控制位
BIT_WRTC1 = 1 << 7 # REG_CTRL_CTR2
BIT_WRTC2 = 1 << 2 # REG_CTRL_CTR1
BIT_WRTC3 = 1 << 7 # REG_CTRL_CTR1
#endregion


class SD3078EXCEPTION(BaseException):
	pass


# https://www.whwave.com.cn/SD3078
class SD3078(object):
	IIC_ADDR = 0x32 # 0110010

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

			result.append( self.bcd2dec(data[REG_RTC_YEAR]    & 0x7f) + 2000)
			result.append( self.bcd2dec(data[REG_RTC_MONTH]   & 0x1f))
			result.append( self.bcd2dec(data[REG_RTC_DAY]     & 0x3f))
			result.append( self.bcd2dec(data[REG_RTC_HOUR]    & 0x3f))
			result.append( self.bcd2dec(data[REG_RTC_MINUTE]  & 0x7f))
			result.append( self.bcd2dec(data[REG_RTC_SECOND]  & 0x7f))
			result.append((self.bcd2dec(data[REG_RTC_WEEKDAY] & 0x07) - 1) % 7)

			RTC().datetime((
				result[LOCALTIME_YEAR],
				result[LOCALTIME_MONTH],
				result[LOCALTIME_DAY],
				result[LOCALTIME_WEEKDAY],
				result[LOCALTIME_HOUR],
				result[LOCALTIME_MINUTE],
				result[LOCALTIME_SECOND], 0
			))

	def battery_voltage(self):
		'''获取电池电压数值，返回值 301 表示 3.01 伏'''
		data = self.__read_mem(REG_CTRL_CTR5, 2)
		voltage = ((data[0] & 0x80) << 1) | data[1]

		return voltage

	def device_id(self):
		'''获取芯片唯一 ID'''
		data = self.__read_mem(REG_CHIP_ID, 8)

		return data

	def temperature(self):
		'''
		获取芯片温度数值，包括当前温度、历史最高和最低温度
		@return: [temp, temp_high, temp_low]
		'''
		result = []

		for reg in (REG_TEMP, REG_TEMP_HIS_H, REG_TEMP_HIS_L):
			result.append(int.from_bytes(self.__read_mem(reg), 16))

		for temp in result:
			temp = temp - 256 if temp & 0x80 == 0x80 else temp

		return result

	def temperature_time(self):
		'''
		获取历史最高和最低温度发生时间
		@return ([temp_high_time], [temp_low_time])
		'''
		result = []

		for reg in (REG_HIS_H_MINUTE, REG_HIS_L_MINUTE):
			data = self.__read_mem(reg, 6)

			result.append( self.bcd2dec(data[REG_RTC_YEAR - 1]    & 0x7f) + 2000)
			result.append( self.bcd2dec(data[REG_RTC_MONTH - 1]   & 0x1f))
			result.append( self.bcd2dec(data[REG_RTC_DAY - 1]     & 0x3f))
			result.append((self.bcd2dec(data[REG_RTC_WEEKDAY - 1] & 0x07) - 1) % 7)
			result.append( self.bcd2dec(data[REG_RTC_HOUR - 1]    & 0x3f))
			result.append( self.bcd2dec(data[REG_RTC_MINUTE - 1]  & 0x7f))

		return result[:6], result[6:]

	def user_ram(self, start=0, data=None, length=1):
		'''设置/获取用户 RAM 中的数据'''
		if data is not None:
			if isinstance(data, dict) or\
			   isinstance(data, (tuple, list, str)) and\
			   start + len(data) + REG_USER_RAM_START > REG_USER_RAM_END:
				return

			self.__write_enabled(True)
			self.__write_mem(REG_USER_RAM_START + start, data)
			self.__write_enabled(False)
		else:
			if start + length + REG_USER_RAM_START > REG_USER_RAM_END:
				return

			return self.__read_mem(REG_USER_RAM_START + start, length)


	#region class properties
	@property
	def power_lost(self):
		'''
		获取芯片供电状态，用于判断芯片是否经过校时
		- 掉电后再次上电返回 True
		- 上电后写入数据返回 False
		'''
		return self.__read_mem(REG_CTRL_CTR1)[0] & 0x01

	@property
	def battery_charge_enabled(self):
		data = self.__read_mem(REG_BAT_CHARGE)
		return data & 0x80 == 0x80

	@battery_charge_enabled.setter
	def battery_charge_enabled(self, enabled:bool):
		'''启用/禁用充电功能'''
		data = 0x82 if enabled else 0x00

		self.__write_enabled(True)
		self.__write_mem(REG_BAT_CHARGE, data)
		self.__write_enabled(False)

	@property
	def battery_iic_enabled(self):
		data = self.__read_mem(REG_IIC_CTRL)
		return data & 0x80 == 0x80

	@battery_charge_enabled.setter
	def battery_iic_enabled(self, enabled:bool):
		'''启用/禁用电池模式下 IIC 功能'''
		data = 0x80 if enabled else 0x00

		self.__write_enabled(True)
		self.__write_mem(REG_IIC_CTRL, data)
		self.__write_enabled(False)
	#endregion


	#region tools function
	def __write_mem(self, mem_addr:int, data):
		'''向指定的寄存器写入数据'''
		if isinstance(data, int):
			data = [data]

		self.__i2c.writeto_mem(SD3078.IIC_ADDR, mem_addr, bytearray(data))

	def __read_mem(self, mem_addr:int, nbytes=1):
		'''从指定的寄存器读取数据'''
		return bytearray(self.__i2c.readfrom_mem(SD3078.IIC_ADDR, mem_addr, nbytes))

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

	def bcd2dec(self, bcd:int):
		'''BCD 码转十进制数，范围：0x00~0x99'''
		if not bcd in range(0x00, 0x99):
			return 0

		return (bcd >> 4) * 10 + (bcd & 0x0f)
	#endregion


if __name__ == '__main__':
	import utime

	i2c = SoftI2C(scl=Pin(18), sda=Pin(19))
	sd3078 = SD3078(i2c)

	# utime.localtime()
	# (year, month, mday, hour, minute, second, weekday, yearday)
	datetime = (2023, 6, 30, 12, 31, 20, 4, 0)

	# sd3078.battery_charge_enabled = False
	# sd3078.battery_iic_enabled = False

	show_log = True

	if sd3078.power_lost:
		sd3078.datetime(datetime)

	sd3078.datetime()
	print(f'localtime: {utime.localtime()}')

	bat_vol = sd3078.battery_voltage()
	print(f'battery vol raw: {bat_vol}')
	if show_log: print(f'battery voltage: {bat_vol / 100}v')

	device_id = sd3078.device_id()
	print(f'device id raw: {device_id}')

	if show_log:
		year       = sd3078.bcd2dec(device_id[0]) + 2000
		month      = sd3078.bcd2dec(device_id[1])
		day        = sd3078.bcd2dec(device_id[2])
		machine_id = sd3078.bcd2dec(device_id[3])
		order_1    = sd3078.bcd2dec(device_id[4])
		order_2    = sd3078.bcd2dec(device_id[5])
		order_3    = sd3078.bcd2dec(device_id[6])
		order_4    = sd3078.bcd2dec(device_id[7])

		print(f'Device ID: {" ".join(["%02X" % i for i in device_id])}')
		print(f'- Production Date: {year}{month:02}{day:02}')
		print(f'- Machine ID: {machine_id}')
		print(f'- Production Order: {order_1:02}{order_2:02}')
		print(f'- Order Index: {order_3:02}{order_4:02}')

	temp = sd3078.temperature()
	print(f'temperature raw: {temp}')
	if show_log: print(f'temp: {temp[0]}, temp_high: {temp[1]}, temp_low: {temp[2]}')

	temp_time = sd3078.temperature_time()
	print(f'temperature time raw: {temp_time}')
	if show_log: print(f'temp_high: {temp_time[0]}, temp_low: {temp_time[1]}')

	a, b, c, d, e = ('hello', b'world', b'\x00\x01\x02', [3, 4, 5], 6)

	sd3078.user_ram(00, a)
	sd3078.user_ram(10, b)
	sd3078.user_ram(20, c)
	sd3078.user_ram(30, d)
	sd3078.user_ram(40, e)
	sd3078.user_ram(00, length=len(a))
	sd3078.user_ram(10, length=len(b))
	sd3078.user_ram(20, length=len(c))
	sd3078.user_ram(30, length=len(d))
	sd3078.user_ram(40, length=1)
	sd3078.user_ram(80, length=1) # out of range, no result
