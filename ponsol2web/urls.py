# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/23
__project__ = PonSol2_Web
Fix the Problem, Not the Blame.
'''

from django.urls import path, include
from django.views.generic import TemplateView

from . import views

app_name = "ponsol2"
urlpatterns = [
    path("", views.index, name="index"),
    # path("input/", views.input_seq_aa, name="input"),  # 输入数据
    path("input/index/", TemplateView.as_view(template_name="ponsol2web/predict_index.html"), name="input"),  # 输入数据
    path("input/sequence/", views.input_seq, name="seq-predict"),  # 通过序列预测
    path("input/id/", views.input_protein_id, name="seq-id"),  # 通过id预测
    path("input/protein/", views.input_protein, name="protein-predict"),  # 通过id预测
    path("predict/seq/", views.predict_seq, name="predict-seq"),  # 预测
    path("predict/ids/", views.predict_ids, name="predict-ids"),
    path("predict/protein/", views.predict_protein, name="predict-protein"),

    # result
    path("task/", views.task_list, name="task-list"),
    path("task/<int:task_id>", views.task_detail, name="task-detail"),
    path("record/<int:record_id>", views.record_detail, name="record-detail"),
    path("task/protein/<int:record_id>", views.protein_detail, name="protein_detail"),

    # about
    path("about/", views.get_about, name="about"),
    path("disclaimer/", TemplateView.as_view(template_name="ponsol2web/disclaimer.html"), name="disclaimer"),

    path("task/running/", views.get_running_tasks, name="task-running"),
    path("task/email/", views.get_running_mail, name="mail-running"),
    # download
    path("download/ponsol2_dataset", views.download_dataset_ponsol2, name="download-dataset-ponsol2"),
    path("download/ponsol_dataset", views.download_dataset_ponsol, name="download-dataset-ponsol"),
    path("download/example/input_fasta_seq", views.download_example_input_fasta_seq,
         name="download-example-input-fasta-seq"),
    path("download/example/input_fasta_aa", views.download_example_input_aas,
         name="download-example-input-fasta-aa"),
    path("download/example/input_fasta_id", views.download_example_input_aa_and_id,
         name="download-example-input-fasta-id"),

    # account
    path("accounts/", include("django.contrib.auth.urls")),
]
