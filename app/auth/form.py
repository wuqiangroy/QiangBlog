#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from wtforms import Form, StringField, validators


class LoginForm(Form):
    """登錄表單"""

    name = StringField("姓名", [validators.required()])
    password = StringField("密碼", [validators.required()])


class RegisterForm(Form):
    """注冊表單"""

    pass
