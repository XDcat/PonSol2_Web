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
import traceback
import pdfkit

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import loader

from PonSol2_Web.settings import DEBUG, EMAIL_HOST_USER
from .ThreadPool import global_mail_thread_pool
from . import models
import pdfkit
from django.urls import reverse

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
    to_mail = task.mail
    if to_mail:
        message = loader.render_to_string("ponsol2web/email/email.html",
                                          {
                                              "url": f" ({RESULT_URL_PRE}/task/{task_id})",
                                              "task": task,
                                          })
        pdf = generatePDF(task) if task.status != "error" else None
        log.debug("单独使用邮件线程池，发送邮件")
        # 发给用户
        global_mail_thread_pool.add_task(f"mail_{task_id}", _send_mail, task, message, to_mail,
                                         "Result of PON-Sol2 - Task{}".format(task.id), 30, pdf=pdf)
        # 发给管理员
        # 没有 pdf
        global_mail_thread_pool.add_task(f"mail_{task_id}_au", _send_mail, task, message, AUTHOR_EMAIL,
                                         "Result of PON-Sol2 - Task{} -> {}".format(task.id, to_mail), 60, )


def _send_mail(task, msg, to_mail, subject="Result of PON-Sol2", sleep_time=10, pdf=None):
    if not isinstance(to_mail, (list, tuple)):
        to_mail = [to_mail, ]
    log.info("发送邮件: %s\n%s\n%s", to_mail, subject, textwrap.shorten(msg, 100))
    try:
        mail = EmailMultiAlternatives(subject, from_email=FROM_EMAIL, to=to_mail)
        mail.attach_alternative(msg, "text/html")
        if pdf:
            mail.attach(subject + ".pdf", pdf)
        mail.content_subtype = "plain"
        res = mail.send()
        if task.email_res:
            task.email_res += str(res)
        else:
            task.email_res = str(res)
        task.save()
        log.info("发送邮件结果: %s", res)
        sleep_time = random.randint(max(0, sleep_time - 5), sleep_time + 5)
        log.info("休眠%s秒", sleep_time)
        time.sleep(sleep_time)
    except Exception:
        msg = traceback.format_exc()
        log.warning("发送邮件失败: %s", traceback.format_exc())
        if task.email_res:
            task.email_res += str(msg)
        else:
            task.email_res = str(msg)
        task.save()


def generatePDF(task):
    log.info("生成 pdf")
    # 生成 pdf 并返回
    pdf = pdfkit.from_url(
        "http://127.0.0.1:80" + reverse("ponsol2:task-detail", args=(task.id,)) + "?type=email",
        False)
    log.info("生成 pdf 完成！")
    return pdf
