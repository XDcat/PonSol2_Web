# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/23
__project__ = PonSol2_Web
Fix the Problem, Not the Blame.
'''

from django.urls import path, include, reverse
from django.views.generic import TemplateView
import django.contrib.auth.views as auth_views

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

    path("task/running/", views.get_running_tasks, name="task-running"),
    # download
    path("download/ponsol2_dataset", views.download_dataset_ponsol2, name="download-dataset-ponsol2"),
    path("download/ponsol_dataset", views.download_dataset_ponsol, name="download-dataset-ponsol"),

    # account
    path("accounts/register/", views.register, name='register'),
    # path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),  # 登录
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),  # 登出

    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),  # 登陆后修改密码
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),  # 登录后修改密码完成

    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        success_url="/accounts/password_reset/done/",
    ), name='password_reset'),  # 未登录，修改密码，发送邮件
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),  # 未登录，修改密码，发送邮件后跳转
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url="/accounts/reset/done/",
    ), name='password_reset_confirm'),  # 未登录，修改密码，邮件中的连接打开后
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),  # 未登录，修改密码，打开邮件的连接后

]
