import urllib.request
import importlib
import json
import datetime
import smtplib
import config as cfg

LAST_NOTIFICATION = None

def email():

	if cfg.ssl:

		try:
			server = smtplib.SMTP_SSL(cfg.smtp_server, cfg.port, timeout=10)
			server.login(cfg.account, cfg.password)
		except Exception as e:
			print(e)
			return

	else:

		try:
			server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)

			if cfg.tls:
				server.starttls()

			server.login(cfg.account, cfg.password)

		except Exception as e:
			print(e)
			return

	message = 'Subject: {}\n\n{}'.format(cfg.subject, cfg.message)
	server.sendmail(cfg.account, cfg.receiver, message)
	server.quit()

class ServerCommunicator:

	def addHeaders(self, request, headers):

		for k, v in headers.items():
			request.add_header(k, v)

	def sendRequest(self, request):

		try:
			response = urllib.request.urlopen(request)

			if response.status >= 200 <= 299:
				return json.loads(response.read() )

		except Exception as e:
			print(f'{e}')

	def createRequest(self, url, headers={}, data=None, origin_req_host=None, unverifiable=False, method=None):
		if data: data = json.dumps(data).encode('utf8')
		request = urllib.request.Request(url, headers=headers, data=data, origin_req_host=origin_req_host, unverifiable=unverifiable, method=method)
		self.addHeaders(request, headers)
		return self.sendRequest(request)

class PushBullet(ServerCommunicator):
	DEVICES_URL = 'https://api.pushbullet.com/v2/devices'
	PUSH_URL = 'https://api.pushbullet.com/v2/pushes'

	def __init__(self):
		self.token = cfg.pushbullet_token
		self.title = cfg.subject
		self.body = cfg.message
		self.specificDevices = cfg.specific_devices
		self.headers = {'Access-Token': self.token, 'Content-Type': 'application/json'}

	def getDevices(self):
		response = self.createRequest(self.DEVICES_URL, self.headers)
		if response: return {x['nickname']: x['iden'] for x in response['devices']}

	def pushMessage(self):
		devices = self.getDevices()

		if devices:

			for name, id in devices.items():

				if self.specificDevices and name not in self.specificDevices:
					continue

				data = {'device_iden': id, 'type': 'note', 'title': self.title, 'body': self.body}
				self.createRequest(self.PUSH_URL, self.headers, data)

class Telegram(ServerCommunicator):
	BOT_URL = 'https://api.telegram.org/bot'

	def __init__(self):
		self.token = cfg.telegram_token
		self.chatId  = cfg.chat_id
		self.message = cfg.message
		self.url = self.BOT_URL + self.token
		self.headers = {'Content-Type': 'application/json'}

	def sendMessage(self):
		data = {'chat_id': self.chatId, 'text': self.message}
		self.createRequest(self.url + '/sendMessage', self.headers, data)

class Slack(ServerCommunicator):
	CONVERSATIONS_URL = 'https://slack.com/api/conversations.list'
	MESSAGE_URL = 'https://slack.com/api/chat.postMessage'

	def __init__(self):
		self.token = cfg.slack_token
		self.message = cfg.message
		self.specificChannels = cfg.specific_channels
		self.headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}

	def getChatRooms(self):
		response = self.createRequest(self.CONVERSATIONS_URL, self.headers)
		if response: return {x['name']: x['id'] for x in response['channels']}

	def sendMessage(self):
		chatrooms = self.getChatRooms()

		if chatrooms:

			for name, id in chatrooms.items():

				if self.specificChannels and name not in self.specificChannels:
					continue

				data = {"channel": id, "text": self.message}
				response = self.createRequest(self.MESSAGE_URL, self.headers, data)

				if not response['ok']:
					print(f"Permission error - Please enable: {response['needed']}")
					return

def message(test=False):
	importlib.reload(cfg)
	global LAST_NOTIFICATION

	if not test and LAST_NOTIFICATION:
		period = datetime.datetime.now() - LAST_NOTIFICATION

		if period < datetime.timedelta(minutes=cfg.interval):
			return

	if cfg.enable_email:
		email()

	if cfg.enable_pushbullet:
		pushbullet = PushBullet()
		pushbullet.pushMessage()

	if cfg.enable_telegram:
		telegram = Telegram()
		telegram.sendMessage()

	if cfg.enable_slack:
		slack = Slack()
		slack.sendMessage()

	if not test:
		LAST_NOTIFICATION = datetime.datetime.now()

if __name__ == "__main__":
	message(test=True)
