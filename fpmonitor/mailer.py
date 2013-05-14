import smtplib
import string

from fpmonitor.consts import *
from django.conf import settings


def send_reboot_mail(node):

    text = "According to your records your node [%s] has been reboted\n" % node.name
    to = []
    for email in node.get_alerting_addresses():
        to.append(email.email)

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


def send_alerting_mail(node, status_from):

    text = "Your node's [%s] status has been changed from %s to %s\n" % (node.name, node.cls_get_status_text(status_from), node.cls_get_status_text(node.status))
    to = []
    for email in node.get_alerting_addresses():
        to.append(email.email)

    body = string.join((
                       "From: %s" % settings.MAIL_FROM,
                       "To: %s" % to,
                       "Subject: %s [%s] %s status" % (settings.SUBJECT_PREFIX, node.cls_get_status_text(node.status), node.name),
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
