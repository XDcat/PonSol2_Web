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
import threading
from ponsol2 import get_seq
from .ThreadPool import global_thred_pool

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


def input_seq(request):
    record_count = Record.objects.count()
    return render(request, "ponsol2web/input_seq_aa.html", {"record_count": record_count})


def input_protein_id(request):
    return render(request, "ponsol2web/input_protein_id.html")


def predict_seq(request):
    """predict: input sequences"""
    log.debug("predict: input sequences")
    task = None
    try:
        # get input
        log.debug("get input")
        ip = get_ip(request)
        mail = request.POST["mail"]
        input_sequence = request.POST["seq"]
        input_aa = request.POST["aa"]
        log.debug("request.POST = \n%s", request.POST)
        # create task
        task = Task.objects.create(ip=ip, mail=mail, status="running")
        task.save()
        log.debug("creat task, id = %s", task.id)
        # check seq and aa
        log.debug("check seq and aa")
        names, seqs, aas = check_seq_input(input_sequence, input_aa)
        log.debug(
            "names, seqs, aas\nnames %s %s\nseqs %s %s\naas %s %s",
            len(names), names, len(seqs), seqs, len(aas), aas
        )
        if len(seqs) == len(aas):
            log.debug("start predicting using thread pool: %s", global_thred_pool)
            global_thred_pool.add_task(task.id, predict, task, names, seqs, aas)
        else:
            task.status = "error"
            task.finish_time = datetime.now().ctime()
            task.error_msg = "The number of sequences doesn't correspond to the number of rows of amino acid substitution."
            task.save()
        return HttpResponseRedirect(reverse("ponsol2:task-detail", args=(task.id,)))
    except Exception as e:
        log.warning("There are some errors with input. Please have a check.")
        log.info(traceback.format_exc())
        log.info(e)
        if task:
            task.status = "error"
            task.finish_time = datetime.now().ctime()
            task.error_msg = "There are some errors with input. Please have a check."
            task.save()
        return HttpResponse("There are some errors with input. Please have a check.")


def predict_ids(request):
    """predict: input ids"""
    log.debug("predict: input ids")
    task = None
    try:
        # get input
        log.debug("get input")
        ip = get_ip(request)
        mail = request.POST["mail"]
        input_seq = request.POST["seq"]
        input_type = request.POST["type"]  # gi, ensembl id, uniprot id
        log.debug("request.POST = \n%s", request.POST)
        # create task
        task = Task.objects.create(ip=ip, mail=mail, status="running")
        task.save()
        log.debug("creat task, id = %s", task.id)
        # check seq and aa
        log.debug("check seq and aa")
        names, seqs, aas = check_ids_input(input_seq, input_type)
        log.debug(
            "names, seqs, aas\nnames %s %s\nseqs %s %s\naas %s %s",
            len(names), names, len(seqs), seqs, len(aas), aas
        )
        if len(seqs) == len(aas):
            log.debug("start predicting using thread pool: %s", global_thred_pool)
            global_thred_pool.add_task(task.id, predict, task, names, seqs, aas)
        else:
            task.status = "error"
            task.error_msg = "The number of sequences doesn't correspond to the number of rows of amino acid substitution."
            task.finish_time = datetime.now().ctime()
            task.save()
        return HttpResponseRedirect(reverse("ponsol2:task-detail", args=(task.id,)))
    except Exception as e:
        log.warning("There are some errors with input. Please have a check.")
        log.info(traceback.format_exc())
        log.info(e)
        if task:
            task.status = "error"
            task.finish_time = datetime.now().ctime()
            task.error_msg = "There are some errors with input. Please have a check."
            task.save()
        return HttpResponse("There are some errors with input. Please have a check.")


def get_detail(request, record_id):
    record = get_object_or_404(Record, pk=record_id)
    return render(request, "ponsol2web/detail.html", {"record": record})


def get_about(request):
    return render(request, "ponsol2web/about.html", None)


def get_running_tasks(request):
    l = global_thred_pool.check_future()
    if l:
        l = str(l)
    else:
        l = "There is no running task."
    return HttpResponse(l)


# --- utils ---
def predict(task, name, seq, aa):
    """
    predict aa of seq
    :param task: corresponding tast
    :param seq: list - seq list
    :param aa: 2d list - each seq has one list that containing some aas
    :return:
    """
    if len(name) != len(seq) or len(seq) != len(aa):
        if len(name) != len(seq):
            msg = "The number of sequences doesn't correspond to the number of names."
            task.status = "error"
            task.error_msg = msg
            task.save()
            raise RuntimeError(msg)
        else:
            msg = "The number of sequences doesn't correspond to the number of rows of amino acid substitution."
            task.status = "error"
            task.error_msg = msg
            task.save()
            raise RuntimeError(msg)
    N = len(seq)
    classifier = PonsolClassifier.PonSol2()
    for i in range(N):
        # initialize record
        n = name[i]
        s = seq[i]
        for a in aa[i]:
            record = task.record_set.create(name=n, seq=s, aa=a)
            record.save()
            # predict
            try:
                pred = classifier.predict(s, a)[0]
                record.solubility = pred
                record.status = "finished"
                record.save()
            except Exception as e:
                record.status = "error"
                record.error_msg = str(e)
                record.save()
    task.status = "finished"
    task.finish_time = datetime.now().ctime()
    task.save()


def check_seq_input(seq, aa):
    # find all sequences
    seqs = re.findall(">[^>]*", seq)
    # find names and sequences
    name_res = []
    seq_res = []
    for seq in seqs:
        rows = seq.split("\n")
        name = rows[0]
        seq = "".join([i.strip() for i in rows[1:]])
        name_res.append(name.strip())
        seq_res.append(seq.strip())
    # find all AAS
    aa = aa.strip()
    aa_res = []
    for row in aa.split("\n"):
        aa_res.append(row.split())

    return name_res, seq_res, aa_res


def check_ids_input(ids, kind):
    """check ids input"""
    ids = ids.strip()
    name_res = []
    seq_res = []
    aa_res = []
    for row in ids.split("\n"):
        row = row.strip()
        if row:
            elements = row.split()
            if len(elements) >= 2:
                seq_id = elements[0]
                aas = elements[1:]
                name, seq = get_seq.get_seq_by_id(seq_id, kind)
                name_res.append(name)
                seq_res.append(seq)
                aa_res.append(aas)
    return name_res, seq_res, aa_res


def task_list(request):
    """return the list of task by ip"""
    ip = get_ip(request)
    tasks = Task.objects.filter(ip=ip)
    return render(request, "ponsol2web/task_list.html", {"tasks": tasks})


def task_detail(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, "ponsol2web/task_detail.html", {"task": task})


def record_detail(request, record_id):
    record = Record.objects.get(id=record_id)
    return render(request, "ponsol2web/record_detail.html", {"record": record})
