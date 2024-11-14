"""
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ws2812-led-clock
"""
from microWebSrv import MicroWebSrv
from microDNSSrv import MicroDNSSrv
from wifihandler import WifiHandler
from config import Config

html =\
'''
<!doctype html>
<html lang="zh-CN">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
		<meta http-equiv="X-UA-Compatible" content="ie=edge">
		<title>WS2812 Led Clock</title>
		<style type='text/css'>
			html {{background-color: floralwhite;}}
			body {{background-color: white;}}
			select {{width: 100%; border: 1px solid grey; height: 30px;}}
			.button {{width: 45%; line-height: 30px; height: 30px;}}
			.buttons {{margin-top: 30px; display: flex; justify-content: space-between;}}
			.password {{display: block; width: -webkit-fill-available; height: 24px;}}
			.container {{border: 1px solid gray; box-shadow: 2px 2px 6px 0px; padding: 10px; border-radius: 4px;}}
			.status {{width: 100%; margin-top: 10px; height: 10px;}}
			.connected {{background-color: forestgreen;}}
			.disconnected {{background-color: tomato;}}
		</style>
	</head>
	<body>
		<div class='container'>
			<form action='/' method='post'>
				<div>
					<label>SSID</label>
					<select name='ssid'>
					{}
					</select>
				</div>
				<div style='margin-top: 10px;'>
					<label>Password</label>
					<input class=password type='password' name='password'>
				</div>

				<div class='buttons'>
					<input class='button' type='submit' value='Submit'>
					<input class='button' type='button' value='Refresh' onclick='location.reload();'>
				</div>
			</form>

			<div class='status {}'></div>
		</div>
	</body>
</html>
'''

def get_wifi_list():
	import network
	sta = network.WLAN(network.STA_IF)
	sta.active(True)

	wifi_list = sta.scan()
	return wifi_list

@MicroWebSrv.route('/', 'POST')
def submit(httpClient, httpResponse):
	data  = httpClient.ReadRequestPostedFormData()
	ssid = data["ssid"]
	password  = data["password"]

	print(data)
	httpResponse.WriteResponseRedirect('/')

@MicroWebSrv.route('/')
def home(httpClient, httpResponse):
	wifi_list = get_wifi_list()
	wifi_list_options = ''

	for wifi in wifi_list:
		wifi = wifi[0].decode()
		wifi_list_options += f'<option value={wifi}>{wifi}</option>'

	httpResponse.WriteResponseOk(
		headers = None,
		contentType	= "text/html",
		contentCharset = "UTF-8",
		content = html.format(wifi_list_options, 'connected' if WifiHandler.is_sta_connected() else 'disconnected')
	)

web = MicroWebSrv(port=Config.WIFI.AP_PORT, webPath= '/')
web.Start(threaded=True)

dns = MicroDNSSrv()
dns.SetDomainsList(Config.WIFI.AP_PORTAL)
dns.Start()

WifiHandler.set_ap_mode()
