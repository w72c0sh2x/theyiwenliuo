<h1 align="center">MicroPython WS2812 Led Clock</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

### 项目介绍

基于`安信可ESP-C3-12F`模组，搭配`WS2812`矩阵灯珠，用于显示当前时间

### 硬件介绍

硬件电路使用 [立创EDA](https://lceda.cn/) 设计，完全适合新手小白使用，PCB 板是在 [深圳嘉立创](https://www.jlc.com/) 下单打样的，本着薅羊毛的原则，板子尺寸限制在了`10cm * 10cm`以内，原理图文件可以在 [立创开源硬件平台](https://oshwhub.com/Walkline/kou-sou-dian-zhen-shi-zhong) 查看，这里不再赘述

> 主控模组选用了`安信可 ESP-C3-12F`，并非常用的`ESP32-WROOM-32D`

### 软件介绍

### 关于配网

`MicroPython`不提供`SmartConfig`相关功能，也就是`Touch`和`AirKiss`配网功能，尝试了把`IDF`示例代码编译到固件中调用，目前已经可以使用以上两种方式进行配网了

> `Touch`方式需要使用乐鑫提供的 [EspTouch for Android](https://github.com/EspressifApp/EsptouchForAndroid/releases)

项目中提供的固件已经集成了半血版`SmartConfig`，用微信或 app 配网时不会提示配网成功，只用于获取`ssid`和`password`，使用方法和代码如下：

```python
from utime import sleep
import network
import smartconfig

station = network.WLAN(network.STA_IF)
station.active(True)

smartconfig.start()

# 关注 安信可科技 微信公众号，点击 应用开发→微信配网，或
# 关注 乐鑫信息科技 微信公众号，点击 商铺→Airkiss 设备
# 输入 Wi-Fi密码 后点击 连接，等待即可

while not smartconfig.success():
    sleep(0.5)

print(smartconfig.info())

# 强制退出 微信配网 或 Airkiss 设备

>>> ('ssid', 'password')
```

### Led 显示

### 相关项目

* [MicroPython WS2812 Research](https://gitee.com/walkline/micropython-ws2812-research)

### 合作交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
	* 走线物联：[163271910](https://jq.qq.com/?_wv=1027&k=xtPoHgwL)
	* 扇贝物联：[31324057](https://jq.qq.com/?_wv=1027&k=yp4FrpWh)

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
