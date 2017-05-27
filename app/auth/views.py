#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import request, redirect, url_for, flash, render_template
from flask_login import login_user, login_required, logout_user, current_user

from app import db
from app.models import User, InviteCode
from app.util import send_mail
from . import auth
from .form import LoginForm, RegisterForm, ChangePasswordForm, ChangeEmailForm, \
    ResetPassword, SendCodeForm


@auth.route("/login", methods=["get", "post"])
def login():
    """登录"""

    form = LoginForm()
    if form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("账户名或密码错误")
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["get", "post"])
def register():
    """注册"""

    form = RegisterForm()
    if form.validate():
        invitation = form.invitation.data
        code = InviteCode.query.filter_by(invitation=invitation).first()
        if not code:
            flash("邀请码不正确，请输入正确的邀请码")
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                invitation=invitation
                )
            db.session.delete(code)
            db.session.add(user)
            db.session.commit()
            flash("现在可以登录了")
        return redirect(url_for("login"))
    return render_template("auth/register.html", form=form)


@login_required
@auth.route("/logout")
def logou():
    """退出登录"""

    logout_user()
    flash("你已经退出了")
    return redirect(url_for("main.index"))


@login_required
@auth.route("/change/password", methods=["get", "post"])
def change_password():
    """更改密码"""

    form = ChangePasswordForm()
    if form.validate():
        if current_user.verify_password(form.password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash("密码已修改")
            return redirect(url_for("logout"))
        else:
            flash("密码错误")
    return render_template("auth/change_password.html", form=form)


@login_required
@auth.route("/change/email", methods=["get", "post"])
def change_email():
    """更改email"""

    form = ChangeEmailForm()
    if form.validate():
        if current_user.verify_password(form.password.data):
            current_user.email = form.email.data
            db.session.add(current_user)
            db.session.commit()
            flash("邮箱已修改")
        else:
            flash("密码错误")
    return render_template("auth/change_email.html", form=form)


@auth.route("/reset/password/sendcode", methods=["get", 'post'])
def send_code():
    """发送验证码"""

    form = SendCodeForm()
    if form.validate():
        user = User.query.filter_by(username=form.username.data).fiest()
        if user and user.email == form.email.data:
            send_mail(receiver=form.email.data)
        flash("一封邮件已经发送至{}， 请复制并填写到重置密码的验证码中。")
        return redirect(url_for("reset_password"))
    return render_template("auth/send_code.html", form=form)


@auth.route("/reset/password", methods=["get", "post"])
def reset_password():
    """重置密码"""

    form = ResetPassword()
    if form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.code == form.code.data:
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
        flash("验证码错误！")
    return render_template("auth/reset_password.html", form=form)
