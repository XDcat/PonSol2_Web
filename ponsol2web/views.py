import logging
import os
import re
import traceback
from datetime import datetime
import json
import tarfile
import pandas as pd

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from ponsol2 import get_seq
from ponsol2 import model as PonsolClassifier
import django.contrib.auth.models as auth_models
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from . import mail_utils
from .ThreadPool import global_thread_pool, global_mail_thread_pool, global_protein_all_thread_pool
from .models import Record, Task
from .forms import RegisterForm, AccountInformationForm

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
        if request.user.is_authenticated:
            user = request.user
            task.user_id = user.id
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
            global_thred_pool.add_task(task.id, predict, task.id, names, seqs, aas)
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
        if request.user.is_authenticated:
            user = request.user
            task.user_id = user.id
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
        task = Task.objects.create(ip=ip, mail=mail, status="running", input_type="protein")
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
        if input_id_type is not None and pid is not None:
            input_type = input_id_type
        else:
            input_type = "seq"
        log.debug("start predicting using thread pool: %s", global_thread_pool)
        global_protein_all_thread_pool.add_task(task.id, predict, task.id, names, seqs, aas, input_type.lower(), ids)
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
        else:
            msg = "The number of sequences doesn't correspond to the number of rows of amino acid substitution."
            task.status = "error"
            task.error_msg = msg
            task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task.save()
    elif len(seq) == 0 or sum(map(lambda x: x != [], aa)) == 0:
        # 没有序列 或者 aa 为空
        msg = "There is no valid input. Please check whether all variations can be matched to input FASTA sequence."
        task.status = "error"
        task.error_msg = msg
        task.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task.save()
    else:
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
                record = Record(task_id=task_id, name=n, seq=s, aa=a, seq_id=identify, seq_id_type=kind)
                records.append(record)
        # log.debug("bulk create")
        # Record.objects.bulk_create(records)
        log.debug("start predict")
        for i, record in enumerate(records):
            # predict
            s = record.seq
            a = record.aa
            log.debug("start %s", a)
            try:
                pred = classifier.predict(s, a)[0]
                record.solubility = pred
                record.status = "finished"
                # record.save()
            except Exception as e:
                record.status = "error"
                record.error_msg = str(e)
                # record.save()
            # if ((i+1) % 20 == 0) or (i == len(records) - 1):
            #     Record.objects.bulk_create(records[i-20 - 1:i+1], 20)
        Record.objects.bulk_create(records)
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
    aa_find = re.findall(">[^>]*", aa.strip())
    name_res = []
    seq_res = []
    if len(seqs) == 0:
        # 正则无法匹配到，尝试当前字串为序列
        seqs = re.sub("\s", "", seq)
        if len(set(list(seqs)) - set(A_LIST)) == 0:
            # 当前 seqs 只由 氨基酸组成
            name_res = ["No name"]
            seq_res = [seqs]
    else:
        for seq in seqs:
            rows = seq.split("\n")
            name = rows[0].strip()
            seq = "".join([i.strip() for i in rows[1:]])
            name_res.append(name.strip())
            seq_res.append(seq.strip())
    # find all AAS
    if len(aa_find) == 0:
        # 正则没有匹配到，认为所有行为替换
        aa_res = []
        for i in aa.split("\n"):
            i = i.strip()
            if len(i) >= 3:
                if i[0] in A_LIST and i[-1] in A_LIST and i[1: -1].isdigit():
                    aa_res.append(i)
        aa_res = [aa_res]
    else:
        aa_res_dict = {}
        for i in aa_find:
            row = i.strip().split("\n")
            if len(row) >= 2:
                name = row[0].strip()
                aas = [j.strip() for j in row[1:] if j.strip()]
                # aas = list(set(aas))
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
            # aa_res.append(list(set([i.strip() for i in row[1:] if i.strip()])))
            aas = [j.strip() for j in row[1:] if j.strip()]
            # aas = list(set(aas))
            aa_res.append(aas)
            id_res.append(identify)
    return name_res, seq_res, aa_res, id_res


def check_protein_input(seq, seq_id, seq_id_type):
    log.debug("seq=%s, seq_id=%s, seq_id_type=%s", seq, seq_id, seq_id_type)
    res_name = res_seq = res_id = None
    if seq:
        seq = seq.upper()
        seqs = re.findall(">[^>]*", seq)
        if len(seqs) == 0:
            res_name = "No name provided"
            res_seq = "".join([i.strip() for i in seq])
        elif len(seqs) > 0:
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
    is_email = request.GET.get("type", None)
    task = Task.objects.get(id=task_id)
    id_group, name_group = task.get_record_group()
    data = {"task": task, }
    if task.input_type == "protein":
        # 如果是全序列预测
        try:
            protein_information = task.get_protein_information()
        except Exception as e:
            return HttpResponse("Fatal error! Please contact the administrator.")
        data["protein_info"] = protein_information
        if is_email:
            # 邮件 pdf 的模板页面
            return render(request, "ponsol2web/email/task_detail_for_protein.html", data)
        else:
            # 直接返回界面
            return render(request, "ponsol2web/task_detail_for_protein.html", data)
    else:
        # 普通的预测
        record_group = list(id_group.values()) + list(name_group.values())
        data["record_group"] = record_group
        if is_email:
            # 邮件 pdf 的模板页面
            return render(request, "ponsol2web/email/task_detail.html", data)
        else:
            return render(request, "ponsol2web/task_detail.html", data)


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
    data = {
        "normal_task": global_thread_pool.check_future(),
        "mail": global_mail_thread_pool.check_future(),
        "protein_task": global_protein_all_thread_pool.check_future(),
    }
    data = json.dumps(data)
    return HttpResponse(data)


def get_running_mail(request):
    l = global_mail_thread_pool.check_future()
    if l:
        l = str(l)
    else:
        l = "There is no running task."
    return HttpResponse(l)


def download_db(request):
    project_dir = os.path.dirname(os.path.join(os.path.dirname(__file__), "./../"))
    file_list = []
    # 数据库文件
    file_list.append(
        os.path.join(project_dir, "db.sqlite3")
    )
    # 日志文件
    log_dir = os.path.join(project_dir, "log")
    file_list += [os.path.join(log_dir, i) for i in os.listdir(log_dir)]

    try:
        # 打包文件
        file_name = os.path.join(os.path.dirname(__file__), "./static/ponsol2web/file/db_backpu.tar.gz")
        tar = tarfile.open(file_name, "w:gz")
        for i in file_list:
            tar.add(i, arcname=os.path.basename(i))
        tar.close()

        file = open(file_name, 'rb')
        response = FileResponse(file, content_type="application/x-download")
        return response
    except Exception as e:
       return HttpResponse(traceback.format_exc())


def download_csv(request):
    return None

# 账户相关
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            password = form.cleaned_data["password"]
            user = auth_models.User.objects.create_user(
                username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name)
            login(request, user)

            return HttpResponseRedirect(reverse("ponsol2:index"))
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


# 个人信息
@login_required()
def personal_information(request):
    message = ""
    user = request.user
    if request.method == "POST":
        form = AccountInformationForm(request.POST)
        if form.is_valid():
            user.username = form.cleaned_data["username"]
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()
            message = "Modifications are in effect."

    # 在 form 中填写数据
    default_information = {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    form = AccountInformationForm(
        default_information
    )

    return render(request, "registration/account_setting.html", {"form": form, "message": message})
