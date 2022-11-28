import sys
import json
import logging
import smtplib
import datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

try:
	from importlib import reload
except:
	from imp import reload

import config as cfg

TESTING = False
LAST_NOTIFICATION = None


def email():

	if cfg.ssl:

		try:
			server = smtplib.SMTP_SSL(cfg.smtp_server, cfg.port, timeout=10)
			server.login(cfg.account, cfg.password)
		except Exception as e:

			if TESTING:
				print("Email Error:", e)
			else:
				logging.error("messenger.py: Couldn't send email: " + str(e))

			return

	else:

		try:
			server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)

			if cfg.tls:
				server.starttls()

			server.login(cfg.account, cfg.password)
		except Exception as e:

			if TESTING:
				print("Email Error:", e)
			else:
				logging.error("messenger.py: Couldn't send email: " + str(e))

			return

	message = "Subject: {}\n\n{}".format(cfg.subject, cfg.message)
	server.sendmail(cfg.account, cfg.receiver, message)
	server.quit()


def sendRequest(service, url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None):

	if data:
		data = json.dumps(data).encode("utf8")

	request = Request(
		url,
		data=data,
		headers=headers,
		origin_req_host=origin_req_host,
		unverifiable=unverifiable,
		method=method,
	)

	try:
		response = urlopen(request)
	except URLError as e:

		if TESTING:
			print("{} error: {}".format(service, e.reason))
		else:
			logging.error(
				"messenger.py: Couldn't send notification: {}: {}".format(
					service,
					e.reason,
				)
			)
		return

	if response.getcode() == 200:
		return json.loads(response.read())


class Pushbullet:
	DEVICES_URL = "https://api.pushbullet.com/v2/devices"
	PUSH_URL = "https://api.pushbullet.com/v2/pushes"
	SERVICE = "Pushbullet"

	def __init__(self):
		self.token = cfg.pushbullet_token
		self.title = cfg.subject
		self.body = cfg.message
		self.specificDevices = cfg.specific_devices
		self.headers = {"Access-Token": self.token, "Content-Type": "application/json"}

	def getDevices(self):
		response = sendRequest(self.SERVICE, self.DEVICES_URL, headers=self.headers)

		if response and "devices" in response:
			return {x["nickname"]: x["iden"] for x in response["devices"]}

	def pushMessage(self):
		devices = self.getDevices()

		if not devices:
			return

		for name, id in devices.items():

			if self.specificDevices and name not in self.specificDevices:
				continue

			data = {"device_iden": id, "type": "note", "title": self.title, "body": self.body}
			sendRequest(self.SERVICE, self.PUSH_URL, data, self.headers)


class Telegram:
	BOT_URL = "https://api.telegram.org/bot"
	SERVICE = "Telegram"

	def __init__(self):
		self.token = cfg.telegram_token
		self.chatId = cfg.chat_id
		self.message = cfg.message
		self.url = self.BOT_URL + self.token
		self.headers = {"Content-Type": "application/json"}

	def sendMessage(self):
		data = {"chat_id": self.chatId, "text": self.message}
		sendRequest(self.SERVICE, self.url + "/sendMessage", data, self.headers)


class Slack:
	CONVERSATIONS_URL = "https://slack.com/api/conversations.list"
	MESSAGE_URL = "https://slack.com/api/chat.postMessage"
	SERVICE = "Slack"

	def __init__(self):
		self.token = cfg.slack_token
		self.message = cfg.message
		self.specificChannels = cfg.specific_channels
		self.headers = {"Authorization": "Bearer " + self.token, "Content-Type": "application/json"}

	def getChannels(self):
		response = sendRequest(self.SERVICE, self.CONVERSATIONS_URL, headers=self.headers)

		if response["ok"]:
			return {x["name"]: x["id"] for x in response["channels"]}
		else:

			if TESTING:
				print("{} error: {}".format(self.SERVICE, response["error"]))
			else:
				logging.error(
					"messenger.py: Couldn't send notification: {} error: {}".format(
						self.SERVICE,
						response["error"],
					)
				)

	def sendMessage(self):
		channels = self.getChannels()

		if channels:

			for name, id in channels.items():

				if self.specificChannels and name not in self.specificChannels:
					continue

				data = {"channel": id, "text": self.message}
				response = sendRequest(self.SERVICE, self.MESSAGE_URL, data, self.headers)

				if not response["ok"]:

					if TESTING:
						print("{} error: {}: {}".format(self.SERVICE, response["error"], response["needed"]))
					else:
						logging.error(
							"messenger.py: Couldn't send notification: {} error: {}: {}".format(
								self.SERVICE,
								response["error"],
								response["needed"],
							)
						)

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
	TESTING = True
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
