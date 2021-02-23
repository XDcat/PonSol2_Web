# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/23
__project__ = PonSol2_Web
Fix the Problem, Not the Blame.
'''

from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "ponsol2"
urlpatterns = [
    path("", views.index, name="index"),
    # path("input/", views.input_seq_aa, name="input"),  # 输入数据
    path("input/index/", TemplateView.as_view(template_name="ponsol2web/predict_index.html"), name="input"),  # 输入数据
    path("input/sequence/", views.input_seq, name="seq-predict"),  # 通过序列预测
    path("input/id/", views.input_protein_id, name="seq-id"),  # 通过id预测
    path("predict/seq/", views.predict_seq, name="predict-seq"),  # 预测
    path("predict/ids/", views.predict_ids, name="predict-ids"),

    # result
    path("task/", views.task_list, name="task-list"),
    path("task/<int:task_id>", views.task_detail, name="task-detail"),
    path("record/<int:record_id>", views.record_detail, name="record-detail"),

    path("about/", views.get_about, name="about"),
    path("disclaimer/", TemplateView.as_view(template_name="ponsol2web/disclaimer.html"), name="disclaimer"),

    path("task/running/", views.get_running_tasks, name="task-running")
]
