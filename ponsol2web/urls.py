# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/23
__project__ = PonSol2_Web
Fix the Problem, Not the Blame.
'''

from django.urls import path
from . import views

app_name = "ponsol2"
urlpatterns = [
    path("", views.index, name="index"),
    path("input/", views.input_seq_aa, name="input"),  # 输入数据
    path("predict/", views.predict, name="predict"),  # 预测
    path("result/", views.get_result, name="result"),
    path("detail/<int:record_id>", views.get_detail, name="detail"),
    path("about/", views.get_about, name="about"),
]
