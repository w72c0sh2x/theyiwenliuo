"""
Copyright © 2023 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython_ble_config
"""
__version__ = '0.1.1'
__version_info__ = (0, 1, 1)
print('module ble_config version:', __version__)


import struct
import ubluetooth as bt
from micropython import const


IRQ_CENTRAL_CONNECT	   = const(1)
IRQ_CENTRAL_DISCONNECT = const(2)
IRQ_GATTS_WRITE		   = const(3)

AD_TYPE_FLAGS						 = const(0x01)
AD_TYPE_COMPLETE_LOCAL_NAME			 = const(0x09)
AD_TYPE_16BIT_SERVICE_UUID_COMPLETE	 = const(0x03)
AD_TYPE_32BIT_SERVICE_UUID_COMPLETE	 = const(0x05)
AD_TYPE_128BIT_SERVICE_UUID_COMPLETE = const(0x07)
AD_TYPE_APPEARANCE					 = const(0x19)

UART_UUID  = bt.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
RX_UUID    = bt.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')
TX_UUID    = bt.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
LOCAL_NAME = 'ble-config'

SSID_PREFIX		= b'ssid_'
PASSWORD_PREFIX	= b'pswd_'


class BLEConfig(object):
	def __init__(self, rx_received_cb=None):
		self.__ble = bt.BLE()
		self.__rx_received_cb = rx_received_cb
		self.__conn_handle = None

		self.ssid = ''
		self.password = ''

		self.__ble.active(False)
		self.__ble.active(True)
		print('ble activated')

		self.__ble.config(gap_name=LOCAL_NAME)
		self.__ble.irq(self.__irq)

		self.__adv_payload = self.__advertising_payload(services=(UART_UUID,))
		self.__resp_payload = self.__advertising_payload(name=LOCAL_NAME)

		self.__register_services()
		self.__advertise()

	def __register_services(self):
		UART_SERVICE = (
			UART_UUID, 
			(
				(TX_UUID, bt.FLAG_NOTIFY,),
				(RX_UUID, bt.FLAG_WRITE,),
			),
		)

		(
			(
				self.__tx_handle,
				self.__rx_handle,
			),
		) = self.__ble.gatts_register_services((UART_SERVICE,))

	def __advertise(self, interval_us=500000):
		self.__ble.gap_advertise(None)
		self.__ble.gap_advertise(interval_us, adv_data=self.__adv_payload, resp_data=self.__resp_payload)
		print('advertising...')

	def __irq(self, event, data):
		if event == IRQ_CENTRAL_CONNECT:
			self.__conn_handle, _, addr, = data
			print(f'[{self.__decode_mac(addr)}] connected, handle: {self.__conn_handle}')

			self.__ble.gap_advertise(None)
		elif event == IRQ_CENTRAL_DISCONNECT:
			self.__conn_handle, _, addr, = data
			print(f'[{self.__decode_mac(addr)}] disconnected, handle: {self.__conn_handle}')

			self.__conn_handle = None

			if not self.success():
				self.__advertise()
		elif event == IRQ_GATTS_WRITE:
			conn_handle, value_handle = data

			if conn_handle == self.__conn_handle and value_handle == self.__rx_handle:
				data = bytes(self.__ble.gatts_read(self.__rx_handle))

				if data.startswith(SSID_PREFIX):
					self.ssid = data[len(SSID_PREFIX):].decode('utf-8')
				elif data.startswith(PASSWORD_PREFIX):
					self.password = data[len(PASSWORD_PREFIX):].decode('utf-8')

				if self.__rx_received_cb:
					self.__rx_received_cb(data)

	def __decode_mac(self, addr):
		if isinstance(addr, memoryview):
			addr = bytes(addr)

		assert isinstance(addr, bytes) and len(addr) == 6, ValueError('mac address value error')
		return ':'.join(['%02X' % byte for byte in addr])

	# https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_advertising.py#L24
	def __advertising_payload(limited_disc=False, br_edr=False, name=None, services=None):
		payload = bytearray()

		def _append(adv_type, value):
			nonlocal payload
			payload += struct.pack('BB', len(value) + 1, adv_type) + value

		_append(
			AD_TYPE_FLAGS,
			struct.pack('B', (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04))
		)

		if name:
			_append(AD_TYPE_COMPLETE_LOCAL_NAME, name)

		if services:
			for uuid in services:
				b = bytes(uuid)
				if len(b) == 2:
					_append(AD_TYPE_16BIT_SERVICE_UUID_COMPLETE, b)
				elif len(b) == 4:
					_append(AD_TYPE_32BIT_SERVICE_UUID_COMPLETE, b)
				elif len(b) == 16:
					_append(AD_TYPE_128BIT_SERVICE_UUID_COMPLETE, b)

		return payload

	def success(self) -> bool:
		return len(self.ssid) > 0 and len(self.password) > 0


if __name__ == '__main__':
	import time

	if False:
		# https://www.uuidgenerator.net/version4
		UART_UUID  = bt.UUID('8F88F065-386C-4833-A814-5F70E4FC32D5')
		RX_UUID    = bt.UUID('2AA1BFAC-D238-4309-9D14-AAE3D8B3EA05')
		TX_UUID    = bt.UUID('560BAE5E-647C-4FDB-99AB-A63702D00B3D')
		LOCAL_NAME = 'config_via_ble'

	def rx_received_cb(data):
		print(f'received rx data: {data}')

	bleconfig = BLEConfig(rx_received_cb)

	while not bleconfig.success():
		time.sleep(0.5)

	print(f'ssid: {bleconfig.ssid}, password: {bleconfig.password}')

"""
	import ubluetooth as bt
	import ble_config

	ble_config.UART_UUID  = bt.UUID(...)
	ble_config.RX_UUID    = bt.UUID(...)
	ble_config.TX_UUID    = bt.UUID(...)
	ble_config.LOCAL_NAME = ...

	bleconfig = ble_config.BLEConfig()
"""
