# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/24
__project__ = PonSol2_Web
Fix the Problem, Not the Blame.
'''

from django.core.mail import send_mail
from . import models
import logging
log = logging.getLogger("ponsol2_web.mail")


def send_result(name, seq, aa, pred, to_mail):
    msg = [
        "Faste Sequence:",
        f"{name}\n{seq}",
        f"AAS: {aa}",
        f"result: %s" % dict(models.Record.SOLUBILITY_CHANGE)[str(pred)],
    ]
    msg = "\n".join(msg)
    _send_mail(msg, to_mail, )


def _send_mail(msg, to_mail, subject="Result of Pon-Sol2"):
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
