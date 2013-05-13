import smtplib
import string

from django.conf import settings


def send_reboot_mail(node):

    text = "According to your records your node [%s] has been reboted\n" % node.name
    to = []
    for email in node.get_alerting_addresses():
        to.append(email.email)

    print to
    body = string.join((
                       "From: %s" % settings.MAIL_FROM,
                       "To: %s" % to,
                       "Subject: %s %s has been rebooted" % (settings.SUBJECT_PREFIX, node.name),
                       "",
                       text
                       ), "\r\n")
    try:
        server = smtplib.SMTP("127.0.0.1")
        server.sendmail(settings.MAIL_FROM, to, body)
        server.quit()
        return True
    except:
        return False
