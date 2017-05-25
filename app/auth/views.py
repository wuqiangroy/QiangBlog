#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import request, jsonify

from app.models import User
from .util import hash_password
from .form import LoginForm, RegisterForm


class BaseView():
    pass


class Login(BaseView):
    """登錄"""

    def get(self):
        form = LoginForm(request.args)
        if not form.validate():
            return 0
        username = form.username.data
        user = User.query.filter_by(username=username).first()


class Register(BaseView):
    """注册"""

    def get(self):
        form = RegisterForm(request.args)
        if not form.validate():
            return 0
        username = form.username.data
        email = form.email.data
        password = hash_password(form.password.data)


