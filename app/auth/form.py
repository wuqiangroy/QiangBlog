#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from wtforms import Form, StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import Regexp, required, Length, Email, EqualTo


class LoginForm(Form):
    """登錄表單"""

    username = StringField("用户名", validators=[required()])
    password = PasswordField("密碼", validators=[required()])
    remember_me = BooleanField("记住我")
    submit = SubmitField("登录")


class RegisterForm(Form):
    """注冊表單"""

    username = StringField("用户名", validators=[
        required(), Length(1, 64), Regexp("[A-Za-z][A-Za-z0-9_.]*$",
                                          message="用户名只能是字母、数字、点或下划线")])
    email = StringField("邮箱", validators=[required(), Email()])
    invitation_code = StringField("邀请码", validators=[required()])
    password = PasswordField("密码", validators=[required()])
    password2 = PasswordField("再次输入密码", validators=[required()])
