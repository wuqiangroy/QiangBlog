#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import request, redirect, url_for, flash, render_template
from flask_login import login_user, login_required, logout_user, current_user

from app import db
from app.models import User, InviteCode
from app.util import send_mail
from . import auth
from .form import LoginForm, RegisterForm, ChangePasswordForm, ChangeEmailForm, \
    ResetPasswordRequest, ResetPassword


@auth.before_app_request
def before_request():
    """判断用户邮箱是否验证"""

    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != "auth." \
                and request.endpoint != "static":
            return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    """用户邮箱未验证不能执行访问"""

    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """登录"""

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("账户名或密码错误")
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    """注册"""

    form = RegisterForm()
    if form.validate_on_submit():
        invite_code = form.invite_code.data
        code = InviteCode.query.filter_by(invite_code=invite_code).first()
        if not code:
            flash("邀请码不正确，请输入正确的邀请码")
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                invite_code=invite_code
                )
            db.session.delete(code)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmatiom_token()
            send_mail(user.email, "邮箱确认", "auth/email/confirm",
                      user=user, token=token)
            flash("已往你的邮箱发送了一封邮件，请及时查收。")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("你的邮箱已验证！")
    else:
        flash("验证失败！")
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    """重发确认邮件"""

    token = current_user.generate_confirmatiom_token()
    send_mail(current_user.email, "确认邮箱", "auth/email/confirm",
              user=current_user, token=token)
    flash("已往你的邮箱发送了一封邮件，请及时查收。")
    return redirect(url_for("main.index"))


@auth.route("/logout")
@login_required
def logout():
    """退出登录"""

    logout_user()
    flash("你已经退出了")
    return redirect(url_for("main.index"))


@auth.route("/change/password", methods=["GET", "POST"])
@login_required
def change_password():
    """更改密码"""

    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash("密码已修改")
            logout_user()
            return redirect(url_for("auth.login"))
        else:
            flash("密码错误")
    return render_template("auth/change_password.html", form=form)


@auth.route("/change/email", methods=["GET", "POST"])
@login_required
def change_email_request():
    """更改email请求"""

    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_change_email_token(new_email)
            send_mail(new_email, "确认邮箱", "auth/email/change_email",
                      user=current_user, token=token)
            flash("一封邮件已发送至你的新邮箱，请注意查收。")
            return redirect(url_for("main.index"))
        else:
            flash("密码错误")
    return render_template("auth/change_email.html", form=form)


@auth.route("/change/email/<token>")
@login_required
def change_email(token):
    """更改邮箱"""

    if current_user.change_email(token):
        flash("你的邮箱已更换")
    else:
        flash("未知请求")
    return redirect(url_for("main.index"))


@auth.route("/reset/password", methods=["GET", "POST"])
def reset_password_request():
    """重置密码"""
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = ResetPasswordRequest()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_mail(user.email, "密码重置", "auth/email/reset_password",
                      user=user, token=token)
            flash("重置密码的请求邮件已经发送至你的邮箱，请注意查收。")
            return redirect(url_for("auth.login"))
        flash("邮箱未注册！")
    return render_template("auth/reset_password.html", form=form)


@auth.route("/reset/password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """重置密码"""

    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = ResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("用户不存在")
            return redirect(url_for("main.index"))
        if user.reset_password(token, form.password.data):
            flash("密码已重置")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)
