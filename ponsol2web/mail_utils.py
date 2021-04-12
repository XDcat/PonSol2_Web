# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/24
__project__ = PonSol2_Web
Fix the Problem, Not the Blame.
'''

import logging
import os

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import loader

from PonSol2_Web.settings import DEBUG
from . import models

log = logging.getLogger("ponsol2_web.mail")
if DEBUG:
    RESULT_URL_PRE = "http://127.0.0.1:8000"
else:
    RESULT_URL_PRE = "http://structure.bmc.lu.se/PON-Sol2"
AUTHOR_EMAIL = ["zenglianjie@foxmail.com", ]
FROM_EMAIL = "zenglianjie@111.com"


def send_result(task_id, ):
    # load email template
    dir_path = os.path.dirname(__file__)

    task = models.Task.objects.get(id=task_id)
    to_mail = task.mail
    if to_mail:
        records = task.record_set.all()
        records_info = []
        for i, record in enumerate(records):
            records_info.append(", ".join(map(str, [i + 1, record.name, record.aa,
                                                    record.get_solubility_display() if record.get_solubility_display() else "error"])))

        message = loader.render_to_string("ponsol2web/email-templates.html",
                                          {"res": records_info, "url": f" ({RESULT_URL_PRE}/task/{task_id})"})
        _send_mail(message, to_mail, )
        # 发送给自己
        au_message = loader.render_to_string("ponsol2web/email-templates.html",
                                             {"res": records_info,
                                              "url": f" ({RESULT_URL_PRE}/task/{task_id})",
                                              "to_mail": to_mail,
                                              })
        _send_mail(au_message, AUTHOR_EMAIL, "Result of PON-Sol2 -> {}".format(to_mail))


def _send_mail(msg, to_mail, subject="Result of PON-Sol2"):
    if not isinstance(to_mail, (list, tuple)):
        to_mail = [to_mail, ]
    log.info("发送邮件: %s\n%s\n%s", to_mail, subject, msg)
    mail = EmailMultiAlternatives(subject, from_email=FROM_EMAIL, to=to_mail)
    # res = send_mail(
    #     subject,
    #     msg,
    #     to_mail,
    #     fail_silently=False,
    # )
    mail.attach_alternative(msg, "text/html")
    mail.content_subtype = "plain"
    res = mail.send()
    log.info("发送邮件结果: %s", res)
