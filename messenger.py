import sys
import json
import smtplib
import datetime
import config as cfg
from urllib.request import Request, urlopen

try:
	from importlib import reload
except:
	from imp import reload

LAST_NOTIFICATION = None


def email():

	if cfg.ssl:

		try:
			server = smtplib.SMTP_SSL(cfg.smtp_server, cfg.port, timeout=10)
			server.login(cfg.account, cfg.password)
		except Exception as e:
			print("Email Error:", e)
			return

	else:

		try:
			server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
			if cfg.tls: server.starttls()
			server.login(cfg.account, cfg.password)
		except Exception as e:
			print("Email Error:", e)
			return

	message = "Subject: {}\n\n{}".format(cfg.subject, cfg.message)
	server.sendmail(cfg.account, cfg.receiver, message)
	server.quit()


class ServerCommunicator:

	def sendRequest(self, request):

		try:
			response = urlopen(request)
			if response.getcode() == 200: return json.loads(response.read())
		except Exception as e:
			print(type(self).__name__ + ":", e)

	def createRequest(self, url, headers={}, data=None, origin_req_host=None, unverifiable=False):
		if data: data = json.dumps(data).encode("utf8")
		request = Request(url, headers=headers, data=data, origin_req_host=origin_req_host, unverifiable=unverifiable)
		return self.sendRequest(request)


class Pushbullet(ServerCommunicator):
	DEVICES_URL = "https://api.pushbullet.com/v2/devices"
	PUSH_URL = "https://api.pushbullet.com/v2/pushes"

	def __init__(self):
		self.token = cfg.pushbullet_token
		self.title = cfg.subject
		self.body = cfg.message
		self.specificDevices = cfg.specific_devices
		self.headers = {"Access-Token": self.token, "Content-Type": "application/json"}

	def getDevices(self):
		response = self.createRequest(self.DEVICES_URL, self.headers)
		if response: return {x["nickname"]: x["iden"] for x in response["devices"]}

	def pushMessage(self):
		devices = self.getDevices()

		if devices:

			for name, id in devices.items():

				if self.specificDevices and name not in self.specificDevices:
					continue

				data = {"device_iden": id, "type": "note", "title": self.title, "body": self.body}
				self.createRequest(self.PUSH_URL, self.headers, data)


class Telegram(ServerCommunicator):
	BOT_URL = "https://api.telegram.org/bot"

	def __init__(self):
		self.token = cfg.telegram_token
		self.chatId = cfg.chat_id
		self.message = cfg.message
		self.url = self.BOT_URL + self.token
		self.headers = {"Content-Type": "application/json"}

	def sendMessage(self):
		data = {"chat_id": self.chatId, "text": self.message}
		self.createRequest(self.url + "/sendMessage", self.headers, data)


class Slack(ServerCommunicator):
	CONVERSATIONS_URL = "https://slack.com/api/conversations.list"
	MESSAGE_URL = "https://slack.com/api/chat.postMessage"

	def __init__(self):
		self.token = cfg.slack_token
		self.message = cfg.message
		self.specificChannels = cfg.specific_channels
		self.headers = {"Authorization": "Bearer " + self.token, "Content-Type": "application/json"}

	def getChannels(self):
		response = self.createRequest(self.CONVERSATIONS_URL, self.headers)

		if response["ok"]:
			return {x["name"]: x["id"] for x in response["channels"]}
		else:
			print("Slack credentials are incorrect")

	def sendMessage(self):
		channels = self.getChannels()

		if channels:

			for name, id in channels.items():

				if self.specificChannels and name not in self.specificChannels:
					continue

				data = {"channel": id, "text": self.message}
				response = self.createRequest(self.MESSAGE_URL, self.headers, data)

				if not response["ok"]:
					print("Slack Error: Insufficient permissions - Please enable:", response["needed"])
					return


def message():
	reload(cfg)
	global LAST_NOTIFICATION

	if LAST_NOTIFICATION:
		period = datetime.datetime.now() - LAST_NOTIFICATION

		if period < datetime.timedelta(minutes=cfg.notification_interval):
			return

	if cfg.enable_email:
		email()

	if cfg.enable_pushbullet:
		pushbullet = Pushbullet()
		pushbullet.pushMessage()

	if cfg.enable_telegram:
		telegram = Telegram()
		telegram.sendMessage()

	if cfg.enable_slack:
		slack = Slack()
		slack.sendMessage()

	LAST_NOTIFICATION = datetime.datetime.now()


if __name__ == "__main__":
	args = sys.argv

	if "email" in args:
		email()

	if "pushbullet" in args:
		pushbullet = Pushbullet()
		pushbullet.pushMessage()

	if "telegram" in args:
		telegram = Telegram()
		telegram.sendMessage()

	if "slack" in args:
		slack = Slack()
		slack.sendMessage()
