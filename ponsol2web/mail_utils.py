# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/24
__project__ = PonSol2_Web
Fix the Problem, Not the Blame.
'''

import logging
import os, time, random
import textwrap

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import loader

from PonSol2_Web.settings import DEBUG, EMAIL_HOST_USER
from .ThreadPool import global_mail_thread_pool
from . import models

log = logging.getLogger("ponsol2_web.mail")
if DEBUG:
    RESULT_URL_PRE = "http://127.0.0.1:8000"
else:
    RESULT_URL_PRE = "http://structure.bmc.lu.se/PON-Sol2"
AUTHOR_EMAIL = ["zenglianjie@foxmail.com", ]
FROM_EMAIL = EMAIL_HOST_USER


def send_result(task_id, ):
    # load email template
    task = models.Task.objects.get(id=task_id)
    id_group, name_group = task.get_record_group()
    record_group = list(id_group.values()) + list(name_group.values())
    to_mail = task.mail
    if to_mail:
        records = task.record_set.all()
        records_info = []
        for i, record in enumerate(records):
            records_info.append(", ".join(map(str, [i + 1, record.name, record.aa,
                                                    record.get_solubility_display() if record.get_solubility_display() else "error"])))

        message = loader.render_to_string("ponsol2web/email/email.html",
                                          {
                                              "res": records_info,
                                              "url": f" ({RESULT_URL_PRE}/task/{task_id})",
                                              "task": task,
                                              "record_group": record_group,
                                          })
        global_mail_thread_pool.add_task(f"mail_{task_id}", _send_mail, message, to_mail,
                                         "Result of PON-Sol2 - Task{}".format(task.id), 30)
        # _send_mail(message, to_mail, subject="Result of PON-Sol2 - Task{}".format(task.id))
        # 发送给自己
        global_mail_thread_pool.add_task(f"mail_{task_id}_au", _send_mail, message, AUTHOR_EMAIL,
                                         "Result of PON-Sol2 - Task{} -> {}".format(task.id, to_mail), 60)
        # _send_mail(message, AUTHOR_EMAIL, "Result of PON-Sol2 - Task{} -> {}".format(task.id, to_mail))


def _send_mail(msg, to_mail, subject="Result of PON-Sol2", sleep_time=10):
    if not isinstance(to_mail, (list, tuple)):
        to_mail = [to_mail, ]
    log.info("发送邮件: %s\n%s\n%s", to_mail, subject, textwrap.shorten(msg, 100))
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
    sleep_time = random.randint(max(0, sleep_time - 5), sleep_time + 5)
    log.info("休眠%s秒", sleep_time)
    time.sleep(sleep_time)
