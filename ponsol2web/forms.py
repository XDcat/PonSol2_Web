# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/3/27
__project__ = Ponsol Web
Fix the Problem, Not the Blame.
'''

from django import forms


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=10)
    last_name = forms.CharField(max_length=10)
    username = forms.CharField(max_length=20)
    email = forms.EmailField()
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)


class AccountInformationForm(forms.Form):
    first_name = forms.CharField(max_length=10)
    last_name = forms.CharField(max_length=10 )
    username = forms.CharField(max_length=20)
    email = forms.EmailField()

    first_name.widget.attrs.update({"class": "form-control"})
    last_name.widget.attrs.update({"class": "form-control"})
    username.widget.attrs.update({"class": "form-control"})
    email.widget.attrs.update({"class": "form-control"})
