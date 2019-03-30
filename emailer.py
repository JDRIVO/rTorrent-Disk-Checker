import os, sys, time, smtplib, config as cfg

lock = os.path.dirname(sys.argv[0]) + '/email.txt'

if os.path.isfile(lock):
        quit()
else:

        with open(lock, 'w+') as txt:
                txt.write('1')

try:
        server = smtplib.SMTP_SSL(cfg.smtp_server, cfg.port)
        server.login(cfg.account, cfg.password)
except:
        server = smtplib.SMTP(cfg.smtp_server, cfg.port)
        server.starttls()
        server.login(cfg.account, cfg.password)

message = 'Subject: {}\n\n{}'.format(cfg.subject, cfg.body)
server.sendmail(cfg.account, cfg.receiver, message)
server.quit()

time.sleep(cfg.interval * 60)
os.remove(lock)
