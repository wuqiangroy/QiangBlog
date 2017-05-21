#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import request, jsonify

from .form import LoginForm, RegisterForm


class BaseView():
    pass


class Login(BaseView):
    """登錄"""

    def get(self):
        form = LoginForm(request.args)
        if not form.validate():
            return 0
