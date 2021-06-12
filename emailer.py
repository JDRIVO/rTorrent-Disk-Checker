import datetime
import smtplib
import config as cfg

def email(cache, test=False):

	if not test:

		if cache.lastNotification:
			period = datetime.datetime.now() - cache.lastNotification

			if period < datetime.timedelta(minutes=cfg.interval):
				return

	server = False

	try:

		try:
			server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
			server.starttls()
			server.login(cfg.account, cfg.password)
		except:

			if server:
				server.quit()

			server = smtplib.SMTP_SSL(cfg.smtp_server, cfg.port, timeout=10)
			server.login(cfg.account, cfg.password)
	except:

		if server:
			server.quit()

		server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
		server.login(cfg.account, cfg.password)

	message = 'Subject: {}\n\n{}'.format(cfg.subject, cfg.body)
	server.sendmail(cfg.account, cfg.receiver, message)
	server.quit()

	if not test:
		cache.lastNotification = datetime.datetime.now()

if __name__ == "__main__":
	email(None, test=True)
