from utime import sleep
import network
import socket
import smartconfig


def inet_pton(ip_str:str):
    '''将字符串 IP 地址转换为字节串'''
    ip_bytes = b''
    ip_segs = ip_str.split('.')

    for seg in ip_segs:
        ip_bytes += int(seg).to_bytes(1, 'little')

    return ip_bytes

def send_ack(local_ip, local_mac):
    '''向手机发送配网完成通知'''
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    data = smartconfig.info()[3].to_bytes(1, 'little') + local_mac
    port = 10000 # airkiss 端口号

    if smartconfig.info()[2] == smartconfig.TYPE_ESPTOUCH:
        data += inet_pton(local_ip)
        port = 18266 # esptouch 端口号

    print(
f"""- sending ack:
    type: {'esptouch' if smartconfig.info()[2] == smartconfig.TYPE_ESPTOUCH else 'airkiss'}
    port: {port}
    data: {data}
    length: {len(data)}
"""
    )

    for _ in range(30):
        sleep(0.1)
        try:
            udp.sendto(data, ('255.255.255.255', port))
        except OSError:
            pass

    print('- ack was sent')

station = network.WLAN(network.STA_IF)
station.active(True)
print('- station actived')

print('- start smartconfig...')
smartconfig.start()

# 手机连接 2.4G 无线网络（重要）
# 关注 安信可科技 微信公众号，点击 应用开发→微信配网，或
# 关注 乐鑫信息科技 微信公众号，点击 商铺→Airkiss 设备，或
# 安装 EspTouch app，点击 EspTouch
# 输入 Wi-Fi密码 后点击 连接按钮

print('- waiting for success...')
while not smartconfig.success():
    sleep(0.5)

print('- got sc info')
ssid, password, sc_type, token = smartconfig.info()
print(smartconfig.info())

print('- connecting to wifi...')
station.connect(ssid, password)

while not station.isconnected():
    sleep(0.5)
print('- wifi connected')

while station.ifconfig()[0] == '0.0.0.0':
    sleep(0.5)
print('- got ip')
print(station.ifconfig())

send_ack(station.ifconfig()[0], station.config('mac'))
