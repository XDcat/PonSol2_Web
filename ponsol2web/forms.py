# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/3/27
__project__ = Ponsol Web
Fix the Problem, Not the Blame.
'''

from django import forms
import django.contrib.auth.models as auth_model


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = auth_model.User
        fields = ["username", "password", "email", "first_name", "last_name"]
