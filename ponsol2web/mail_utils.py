# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/24
__project__ = PonSol2_Web
Fix the Problem, Not the Blame.
'''

import logging
import os

from django.core.mail import send_mail

from PonSol2_Web.settings import DEBUG
from . import models

log = logging.getLogger("ponsol2_web.mail")
if DEBUG:
    RESULT_URL_PRE = "http://127.0.0.1:8000"
else:
    RESULT_URL_PRE = "http://structure.bmc.lu.se/PON-Sol2"
AUTHOR_EMAIL = ["zenglianjie@foxmail.com"]

def send_result(task_id, ):
    # load email template
    dir_path = os.path.dirname(__file__)
    with open(os.path.join(dir_path, "..", "email-templates.txt")) as f:
        temp = f.read()

    task = models.Task.objects.get(id=task_id)
    to_mail = task.mail
    if to_mail:
        records = task.record_set.all()
        records_info = []
        for i, record in enumerate(records):
            records_info.append("{}. {}, {}, {}".format(i + 1, record.name, record.aa, record.get_solubility_display()))

        res_list = ["\n".join(records_info), ]
        res_list = "\n".join(res_list)
        res_list = temp.format(
            res=res_list,
            url=f" ({RESULT_URL_PRE}/task/{task_id})",
        )
        _send_mail(res_list, to_mail, )
        # 发送给自己
        res_list += "\nThis email is sent to {}".format(to_mail)
        _send_mail(res_list, AUTHOR_EMAIL)


def _send_mail(msg, to_mail, subject="Result of PON-Sol2"):
    if not isinstance(to_mail, (list, tuple)):
        to_mail = [to_mail, ]
    log.info("发送邮件: %s\n%s\n%s", to_mail, subject, msg)
    res = send_mail(
        subject,
        msg,
        "zenglianjie@111.com",
        to_mail,
        fail_silently=False,
    )
    log.info("发送邮件结果: %s", res)
