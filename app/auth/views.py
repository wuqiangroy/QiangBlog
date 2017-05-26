#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import request, jsonify, redirect, url_for, flash, render_template
from flask_login import login_user, login_required, logout_user, current_user

from app.models import User
from . import auth
from .util import hash_password
from .form import LoginForm, RegisterForm


@auth.route("/login", methods=["get", "post"])
def login():
    """登录"""

    form = LoginForm(request.args)
    if form.validate():
        username = form.username.data
        password = hash(form.password.data)
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("账户名或密码错误")
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["get", "post"])
def register():
    """注册"""

    form = RegisterForm(request.args)
    if form.validate():
        username = form.username.data
        email = form.email.data
        password = hash_password(form.password.data)


@login_required
@auth.route("/logout")
def logou():
    """退出"""

    logout_user()
    flash("你已经退出了！")
    return redirect(url_for("main.index"))
