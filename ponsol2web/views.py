import traceback

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Record, Task
from datetime import datetime
import re
from . import mail_utils
import logging
from ponsol2 import model as PonsolClassifier

log = logging.getLogger("ponsol2_web.views")


def get_ip(request):
    ip = None
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        ip = request.META['HTTP_X_FORWARDED_FOR']
    elif "REMOTE_ADDR" in request.META.keys():
        ip = request.META['REMOTE_ADDR']

    return ip


# Create your views here.

def index(request):
    return render(request, "ponsol2web/index.html", None)


def input_seq_aa(request):
    record_count = Record.objects.count()
    return render(request, "ponsol2web/input_seq_aa.html", {"record_count": record_count})


def predict(request):
    record_count = Record.objects.count()
    try:
        # 用户信息
        log.debug("开始预测: request = %s", request)
        ip = get_ip(request)
        mail = request.POST["mail"]
        task = Task.objects.create(ip=ip, mail=mail)
        aa = request.POST["aa"]
        fasta_seq = request.POST["seq"]
        fasta_seq = fasta_seq.split("\n")
        log.info("seq = %s", fasta_seq)
        log.info("aas = %s", aa)
        log.info("task = %s", task)
        name = fasta_seq[0].strip()
        seq = "".join([i.strip() for i in fasta_seq[1:]])
        record = task.record_set.create(name=name, seq=seq, aa=aa)
        task.save()
        # 预测
        classifier = PonsolClassifier.PonSol2()
        pred = classifier.predict(seq, aa)[0]
        record.solubility = pred
        record.save()
        log.info("pred = %s", pred)
        mail_utils.send_result(name, seq, aa, pred, mail)

    except Exception as e:
        log.error(traceback.format_exc())
        return render(
            request, "ponsol2web/input_seq_aa.html",
            {
                "error_message": "Input error: %s" % e,
                "record_count": record_count,
            }
        )
    else:
        return HttpResponseRedirect(reverse("ponsol2:detail", args=(record.id,)))


def get_result(request):
    ip = get_ip(request)
    tasks = Task.objects.filter(ip=ip)
    record_list = []
    for task in tasks:
        for record in task.record_set.all():
            record_list.append(record)

    return render(request, "ponsol2web/result.html", {"record_list": record_list})


def get_detail(request, record_id):
    record = get_object_or_404(Record, pk=record_id)
    return render(request, "ponsol2web/detail.html", {"record": record})


def get_about(request):
    return render(request, "ponsol2web/about.html", None)
