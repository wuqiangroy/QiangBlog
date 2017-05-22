#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from wtforms import Form, StringField, validators


class LoginForm(Form):
    """登錄表單"""

    username = StringField("用户名", [validators.required()])
    password = StringField("密碼", [validators.required()])


class RegisterForm(Form):
    """注冊表單"""

    username = StringField("用户名", [validators.required()])
    email = StringField("邮箱", [validators.required()])
    invitation_code = StringField("邀请码", [validators.required()])
    password = StringField("密码", [validators.required()])
