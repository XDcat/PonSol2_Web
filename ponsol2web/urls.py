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
    # hide
    path("task/", views.task_list, name="task-list"),
    path("task/running/", views.get_running_tasks, name="task-running"),
    path("task/email/template", TemplateView.as_view(template_name="ponsol2web/email/email.html")),
    path("task/email/template/task_detail", TemplateView.as_view(template_name="ponsol2web/email/task_detail.html")),
    path("task/email/", views.get_running_mail, name="mail-running"),
    path("zlj/download/db/", views.download_db, name="download-db"),
    path("zlj/download/csv/", views.download_csv, name="download-db"),

    # index
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
    # path("disclaimer/", TemplateView.as_view(template_name="ponsol2web/disclaimer.html"), name="disclaimer"),

    path("task/running/", views.get_running_tasks, name="task-running"),
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
    # path("accounts/", include("django.contrib.auth.urls")),
    path("download/ponsol_dataset", views.download_dataset_ponsol, name="download-dataset-ponsol"),

    # account
    # path("accounts/setting/", TemplateView.as_view(template_name="registration/setting.html"), name='account-setting'),
    path("accounts/setting/", views.personal_information, name='account-setting'),
    path("accounts/dashboard/", views.dashboard, name="dashboard"),
    # dashboard 的 api
    path("accounts/dashboard/api/task_info", views.api_task_info, name="api-task-info"),
    path("accounts/dashboard/api/record_info", views.api_record_info, name="api-record-info"),

    # 注册 登录 退出登录
    path("accounts/register/", views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name="registration/login.html",
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page="/",
    ), name='logout'),

    # 登录后,修改密码
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # 未登录，修改密码，发送邮件
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name="registration/forgot.html",
        success_url="/accounts/password_reset/done/",
    ), name='password_reset'),

    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="registration/forgot_done.html"
    ), name='password_reset_done'),
    # 重置秘密跳转到的位置
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/forgot_confirm.html",
        success_url="/accounts/reset/done/",
    ), name='password_reset_confirm'),
    # 重置密码完成后
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/forgot_complete.html",
    ), name='password_reset_complete'),
]
