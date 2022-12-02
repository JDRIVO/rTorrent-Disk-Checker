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
		self.devices = cfg.pushbullet_devices
		self.headers = {"Access-Token": self.token, "Content-Type": "application/json"}

	def getDevices(self):
		response = sendRequest(self.SERVICE, self.DEVICES_URL, headers=self.headers)

		if response and "devices" in response:
			return {x["nickname"]: x["iden"] for x in response["devices"]}

	def sendMessage(self):
		devices = self.getDevices()

		if devices:

			for name, id in devices.items():

				if self.devices and name not in self.devices:
					continue

				data = {"device_iden": id, "type": "note", "title": self.title, "body": self.body}
				sendRequest(self.SERVICE, self.PUSH_URL, data, self.headers)


class Pushover:
	PUSH_URL = "https://api.pushover.net/1/messages.json"
	SERVICE = "Pushover"

	def __init__(self):
		self.url = self.PUSH_URL
		self.token = cfg.pushover_token
		self.user = cfg.pushover_user_key
		self.title = cfg.subject
		self.message = cfg.message

		self.devices = cfg.pushover_devices
		self.priority = cfg.pushover_priority
		self.sound = cfg.pushover_sound
		self.headers = {"Content-Type": "application/json"}

	def sendMessage(self):
		data = {
			"token": self.token,
			"user": self.user,
			"title": self.title,
			"message": self.message,
			"device": self.devices,
			"priority": self.priority,
			"sound": self.sound,
		}
		sendRequest(self.SERVICE, self.url, data, self.headers)


class Telegram:
	BOT_URL = "https://api.telegram.org/bot"
	SERVICE = "Telegram"

	def __init__(self):
		self.token = cfg.telegram_token
		self.chatId = cfg.telegram_chat_id
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
		self.channels = cfg.slack_channels
		self.headers = {"Authorization": "Bearer " + self.token, "Content-Type": "application/json"}

	def getChannels(self):
		response = sendRequest(self.SERVICE, self.CONVERSATIONS_URL, headers=self.headers)

		if not response:
			return

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

				if self.channels and name not in self.channels:
					continue

				data = {"channel": id, "text": self.message}
				response = sendRequest(self.SERVICE, self.MESSAGE_URL, data, self.headers)

				if response and not response["ok"]:

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

	LAST_NOTIFICATION = datetime.datetime.now()

	if cfg.enable_email:
		email()

	if cfg.enable_pushbullet:
		pushbullet = Pushbullet()
		pushbullet.sendMessage()

	if cfg.enable_pushover:
		pushover = Pushover()
		pushover.sendMessage()

	if cfg.enable_telegram:
		telegram = Telegram()
		telegram.sendMessage()

	if cfg.enable_slack:
		slack = Slack()
		slack.sendMessage()


if __name__ == "__main__":
	TESTING = True
	args = sys.argv

	if "email" in args:
		email()

	if "pushbullet" in args:
		pushbullet = Pushbullet()
		pushbullet.sendMessage()

	if "pushover" in args:
		pushover = Pushover()
		pushover.sendMessage()

	if "telegram" in args:
		telegram = Telegram()
		telegram.sendMessage()

	if "slack" in args:
		slack = Slack()
		slack.sendMessage()
