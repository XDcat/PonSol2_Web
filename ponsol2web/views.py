import logging
import os
import re
import traceback
from datetime import datetime

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from ponsol2 import get_seq
from ponsol2 import model as PonsolClassifier
from . import mail_utils
from .ThreadPool import global_thread_pool, global_mail_thread_pool
from .models import Record, Task

log = logging.getLogger("ponsol2_web.views")
MAX_FILE_SIZE = 20 * 1024 * 8  # 20MB
MAX_PAGE_NUM = 6
A_LIST = ('A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y')


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
    record_count = Record.objects.count()
    return render(request, "ponsol2web/input_protein_id.html", {"record_count": record_count})


def input_protein(request):
    record_count = Record.objects.count()
    return render(request, "ponsol2web/input_protein.html", {"record_count": record_count})


def predict_seq(request):
    """predict: input sequences"""
    log.debug("predict: input sequences")
    task = None
    error_msg = None
    try:
        # get input
        log.debug("get input")
        ip = get_ip(request)
        mail = request.POST.get("mail", None)

        input_sequence = request.POST["seq"]
        input_aa = request.POST["aa"]
        file_sequence = request.FILES.get("sequenceInputFile")
        file_aa = request.FILES.get("assInputFile")
        if input_sequence and input_aa:
            pass
        elif file_sequence and file_aa:
            if file_sequence.size > MAX_FILE_SIZE or file_aa.size > MAX_FILE_SIZE:
                error_msg = "THe files are too large. Please make sure that each file is less than 20MB."
                raise RuntimeError(error_msg)
            else:
                input_sequence = file_sequence.read().decode("utf-8")
                input_aa = file_aa.read().decode("utf-8")
        else:
            error_msg = "There is an error in the input. " \
                        "This may be due to no input or the fact that both input and file are provided."
            raise RuntimeError(error_msg)

        log.debug("request.POST = \n%s", request.POST)
        # create task
        task = Task.objects.create(ip=ip, mail=mail, status="running", input_type="seq")
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
            log.debug("start predicting using thread pool: %s", global_thread_pool)
            global_thread_pool.add_task(task.id, predict, task.id, names, seqs, aas, )
        else:
            task.status = "error"
            task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task.error_msg = "The number of sequences doesn't correspond to the number of rows of amino acid substitution."
            task.save()
        return HttpResponseRedirect(reverse("ponsol2:task-detail", args=(task.id,)))
    except Exception as e:
        if not error_msg:
            error_msg = "There are some errors with input. Please have a check."
        log.warning(error_msg)
        log.info(traceback.format_exc())
        log.info(e)
        if task:
            task.status = "error"
            task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task.error_msg = error_msg
            task.save()
        return render(request, "ponsol2web/input_seq_aa.html", {"error_msg": error_msg})


def predict_ids(request):
    """predict: input ids"""
    log.debug("predict: input ids")
    task = None
    error_msg = None
    try:
        # get input
        log.debug("get input")
        ip = get_ip(request)
        mail = request.POST.get("mail", None)

        input_sequence = request.POST["seq"]
        file_sequence = request.FILES.get("sequenceInputFile", None)
        input_type = request.POST["type"]  # gi, ensembl id, uniprot id
        if input_sequence:
            pass
        elif file_sequence:
            if file_sequence.size > MAX_FILE_SIZE:
                error_msg = "THe files are too large. Please make sure that each file is less than 20MB."
                raise RuntimeError(error_msg)
            else:
                input_sequence = file_sequence.read().decode("utf-8")
        else:
            error_msg = "There is an error in the input. " \
                        "This may be due to no input or the fact that both input and file are provided."
            raise RuntimeError(error_msg)

        log.debug("request.POST = \n%s", request.POST)
        # create task
        task = Task.objects.create(ip=ip, mail=mail, status="running", input_type="id")
        task.save()
        log.debug("creat task, id = %s", task.id)
        # check seq and aa
        log.debug("check seq and aa")
        try:
            names, seqs, aas, ids = check_ids_input(input_sequence, input_type)
        except Exception as e:
            error_msg = "Can't get FASTA sequence using input id(s). Please check the input id(s)."
            raise RuntimeError(error_msg)
        log.debug(
            "names, seqs, aas\nnames %s %s\nseqs %s %s\naas %s %s",
            len(names), names, len(seqs), seqs, len(aas), aas
        )
        if len(seqs) == len(aas):
            log.debug("start predicting using thread pool: %s", global_thread_pool)
            global_thread_pool.add_task(task.id, predict, task.id, names, seqs, aas, input_type.lower(), ids)
        else:
            task.status = "error"
            task.error_msg = "The number of sequences doesn't correspond to the number of rows of amino acid substitution."
            task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task.save()
        return HttpResponseRedirect(reverse("ponsol2:task-detail", args=(task.id,)))
    except Exception as e:
        if not error_msg:
            error_msg = "There are some errors with input. Please have a check."
        log.warning(error_msg)
        log.info(traceback.format_exc())
        log.info(e)
        if task:
            task.status = "error"
            task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task.error_msg = error_msg
            task.save()
        return render(request, "ponsol2web/input_protein_id.html", {"error_msg": error_msg})


def predict_protein(request):
    log.debug("predict: input protein")
    task = None
    error_msg = None
    try:
        # get input
        log.debug("get input")
        log.debug("request.POST = \n%s", request.POST)
        ip = get_ip(request)
        mail = request.POST.get("mail", None)
        input_sequence = request.POST.get("seq", None)
        input_id = request.POST.get("input_id", None)
        input_id_type = request.POST.get("type", None)
        # create task
        task = Task.objects.create(ip=ip, mail=mail, status="running", input_type="id")
        task.save()
        log.debug("creat task, id = %s", task.id)
        # check seq and aa
        log.debug("check seq and aa")
        try:
            pname, pseq, pid = check_protein_input(input_sequence, input_id, input_id_type)
        except Exception as e:
            error_msg = "No valid input."
            raise RuntimeError(error_msg)
        paa = []
        for i in range(1, len(pseq) + 1):
            a1 = pseq[i - 1]
            for a2 in A_LIST:
                if a2 != a1:
                    one_aa = "{}{}{}".format(a1, i, a2)
                    paa.append(one_aa.upper())
        seqs = [pseq]
        names = [pname]
        aas = [paa]
        ids = [pid]
        log.debug(
            "names, seqs, aas\nnames %s %s\nseqs %s %s\naas %s %s",
            len(names), names, len(seqs), seqs, len(aas), aas
        )
        input_type = "protein"
        log.debug("start predicting using thread pool: %s", global_thread_pool)
        global_thread_pool.add_task(task.id, predict, task.id, names, seqs, aas, input_type.lower(), ids)
        return HttpResponseRedirect(reverse("ponsol2:task-detail", args=(task.id,)))
    except Exception as e:
        if not error_msg:
            error_msg = "There are some errors with input. Please have a check."
        log.warning(error_msg)
        log.info(traceback.format_exc())
        log.info(e)
        if task:
            task.status = "error"
            task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task.error_msg = error_msg
            task.save()
        return render(request, "ponsol2web/input_protein.html", {"error_msg": error_msg})


def get_detail(request, record_id):
    record = get_object_or_404(Record, pk=record_id)
    return render(request, "ponsol2web/detail.html", {"record": record})


def get_about(request):
    return render(request, "ponsol2web/about.html", None)


# --- utils ---
def predict(task_id, name, seq, aa, kind="seq", ids=None):
    """
    predict aa of seq
    :param task_id: id of corresponding tast
    :param seq: list - seq list
    :param aa: 2d list - each seq has one list that containing some aas
    :return:
    """
    log.debug("start the predict task(id = %s)", task_id)
    task = Task.objects.get(id=task_id)
    if len(name) != len(seq) or len(seq) != len(aa):
        if len(name) != len(seq):
            msg = "The number of sequences doesn't correspond to the number of names."
            task.status = "error"
            task.error_msg = msg
            task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task.save()
            raise RuntimeError(msg)
        else:
            msg = "The number of sequences doesn't correspond to the number of rows of amino acid substitution."
            task.status = "error"
            task.error_msg = msg
            task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task.save()
            raise RuntimeError(msg)
    elif len(name) == 0:
        msg = "There is no valid input."
        task.status = "error"
        task.error_msg = msg
        task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task.save()
        raise RuntimeError(msg)

    N = len(seq)
    try:
        log.debug("Load classifier.")
        classifier = PonsolClassifier.PonSol2()
    except Exception as e:
        msg = "Can't load classifier."
        log.warning(msg)
        log.info(traceback.format_exc())
        task.status = "error"
        task.error_msg = str(msg)
        task.save()

    log.debug("create records")
    records = []
    for i in range(N):
        # initialize record
        n = name[i]
        s = seq[i]
        identify = ids[i] if ids else None
        for a in aa[i]:
            # record = task.record_set.create(name=n, seq=s, aa=a, seq_id=identify, seq_id_type=kind)
            # record.save()
            # log.debug(a)
            record = Record(task_id=task_id, name=n, seq=s, aa=a, seq_id=identify, seq_id_type=kind)
            records.append(record)
    log.debug("bulk create")
    Record.objects.bulk_create(records)
    log.debug("start predict")
    for record in records:
        # predict
        s = record.seq
        a = record.aa
        log.debug("start %s", a)
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
    task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    task.save()
    log.debug("task(id=%s) is finished!", task_id)
    try:
        mail_utils.send_result(task.id)
        log.debug(f"Send email successfully. (task id = {task.id})")
    except Exception as e:
        log.debug(f"Failed to send mail.(task id ={task.id})")
        log.debug(traceback.format_exc())


def check_seq_input(seq, aa):
    # find all sequences
    seq = seq.upper()
    aa = aa.upper()
    seqs = re.findall(">[^>]*", seq)
    # find names and sequences
    name_res = []
    seq_res = []
    for seq in seqs:
        rows = seq.split("\n")
        name = rows[0].strip()
        seq = "".join([i.strip() for i in rows[1:]])
        name_res.append(name.strip())
        seq_res.append(seq.strip())
    # find all AAS
    aa_find = re.findall(">[^>]*", aa.strip())
    aa_res_dict = {}
    for i in aa_find:
        row = i.strip().split("\n")
        if len(row) >= 2:
            name = row[0].strip()
            aas = list(set([j.strip() for j in row[1:] if j.strip()]))
            aa_res_dict[name] = aas
    aa_res = [aa_res_dict.get(i, []) for i in name_res]

    return name_res, seq_res, aa_res


def check_ids_input(ids, kind):
    """check ids input"""
    ids = ids.upper().strip()
    kind = kind.lower()
    # find all
    ids_find = re.findall(">[^>]*", ids)
    name_res = []
    seq_res = []
    aa_res = []
    id_res = []
    for row in ids_find:
        row = row.split("\n")
        if len(row) >= 2:
            identify = row[0][1:].strip()
            name, seq = get_seq.get_seq_by_id(identify, kind)
            name_res.append(name)
            seq_res.append(seq)
            aa_res.append(list(set([i.strip() for i in row[1:] if i.strip()])))
            id_res.append(identify)
    return name_res, seq_res, aa_res, id_res


def check_protein_input(seq, seq_id, seq_id_type):
    log.debug("seq=%s, seq_id=%s, seq_id_type=%s", seq, seq_id, seq_id_type)
    res_name = res_seq = res_id = None
    if seq:
        seq = seq.upper()
        seqs = re.findall(">[^>]*", seq)
        if len(seqs) > 0:
            rows = seqs[0].split("\n")
            res_name = rows[0].strip()
            res_seq = "".join([i.strip() for i in rows[1:]])
    elif seq_id and seq_id_type:
        res_id = re.sub("\s|>", "", seq_id)
        res_name, res_seq = get_seq.get_seq_by_id(res_id, seq_id_type)
    else:
        raise RuntimeError("No valid input.")
    return res_name, res_seq, res_id


def task_list(request):
    """return the list of task by ip"""
    ip = get_ip(request)
    tasks = Task.objects.filter(ip=ip).order_by("-start_time")
    # pager
    paginator = Paginator(tasks, 15)
    num_pages = paginator.num_pages
    page_list = paginator.page_range
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    current_page = page_obj.number
    display_page_list = []
    if len(page_list) <= MAX_PAGE_NUM:
        for i in page_list:
            display_page_list.append((i, f"?page={i}"))
    else:
        if current_page <= num_pages - MAX_PAGE_NUM:
            for i in range(current_page, current_page + 4):
                display_page_list.append((i, f"?page={i}"))
            display_page_list.append(("...", "#"))
            for i in range(1, 0 - 1, -1):
                t = num_pages - i
                display_page_list.append((t, f"?page={t}"))
            pass
        else:
            for i in range(num_pages - MAX_PAGE_NUM, num_pages + 1):
                display_page_list.append((i, f"?page={i}"))

    return render(request, "ponsol2web/task_list.html",
                  {"count": num_pages, "page_obj": page_obj, "page_list": display_page_list})


def task_detail(request, task_id):
    task = Task.objects.get(id=task_id)
    id_group, name_group = task.get_record_group()
    record_group = list(id_group.values()) + list(name_group.values())
    return render(request, "ponsol2web/task_detail.html",
                  {"task": task, "record_group": record_group})


def record_detail(request, record_id):
    record = Record.objects.get(id=record_id)
    return render(request, "ponsol2web/record_detail.html", {"record": record})


def download_dataset_ponsol2(request):
    path = os.path.join(os.path.dirname(__file__), "./static/ponsol2web/file/PON-Sol2 dataset.zip")
    file = open(path, 'rb')
    response = FileResponse(file)
    return response


def download_dataset_ponsol(request):
    path = os.path.join(os.path.dirname(__file__), "./static/ponsol2web/file/PON-Sol_data.xlsx")
    file = open(path, 'rb')
    response = FileResponse(file)
    return response


def download_example_input_fasta_seq(request):
    path = os.path.join(os.path.dirname(__file__), "./static/ponsol2web/file/example-FASTA sequence(s).txt")
    file = open(path, 'rb')
    response = FileResponse(file, content_type="application/x-download")
    return response


def download_example_input_aas(request):
    path = os.path.join(os.path.dirname(__file__), "./static/ponsol2web/file/example-Amino acid substitution(s).txt")
    file = open(path, 'rb')
    response = FileResponse(file, content_type="application/x-download")
    return response


def download_example_input_aa_and_id(request):
    path = os.path.join(os.path.dirname(__file__),
                        "./static/ponsol2web/file/example-ID(s) and amino acid substitution(s).txt")
    file = open(path, 'rb')
    response = FileResponse(file, content_type="application/x-download")
    return response


def protein_detail(request, record_id):
    record = Record.objects.get(id=record_id)
    return render(request, "ponsol2web/protein_detail.html", {"record": record})


def get_running_tasks(request):
    l = global_thread_pool.check_future()
    if l:
        l = str(l)
    else:
        l = "There is no running task."
    return HttpResponse(l)


def get_running_mail(request):
    l = global_mail_thread_pool.check_future()
    if l:
        l = str(l)
    else:
        l = "There is no running task."
    return HttpResponse(l)
