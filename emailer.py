import os, sys, datetime, smtplib, config as cfg

lock = os.path.dirname(sys.argv[0]) + '/email.txt'

if os.path.isfile(lock):
        file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getctime(lock))

        if file_age < datetime.timedelta(minutes=cfg.interval):
                quit()

with open(lock, 'w+') as txt:
        txt.write('1')

def send_email():
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

send_email()

if __name__ == '__main__':
        print('\n1st Traceback block is TLS related\n2nd Traceback block is SSL related\n3rd Traceback block is Non TLS/SSL related\n')
        send_email()
