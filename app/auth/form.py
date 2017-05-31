#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import Regexp, required, Length, Email, EqualTo
from wtforms import ValidationError

from app.models import User


class LoginForm(FlaskForm):
    """登录表单"""

    username = StringField("用户名", validators=[required()])
    password = PasswordField("密碼", validators=[required()])
    remember_me = BooleanField("记住我")
    submit = SubmitField("登录")


class RegisterForm(FlaskForm):
    """注冊表单"""

    username = StringField("用户名", validators=[
        required(), Length(1, 64), Regexp("[A-Za-z][A-Za-z0-9_.]*$",
                                          message="用户名只能是字母、数字、点或下划线")
    ])
    email = StringField("邮箱", validators=[required(), Email()])
    invitation = StringField("请输入邀请码", validators=[required()])
    password = PasswordField("密码", validators=[
        required(), EqualTo("password2", message="两次密码不正确")
    ])
    password2 = PasswordField("再次输入密码", validators=[required()])
    submit = SubmitField("提交")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已被占用！")

    def validation_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已注册！")


class ChangePasswordForm(FlaskForm):
    """更改密码表单"""

    password = PasswordField("原始密码", validators=[required()])
    new_password = PasswordField("新密码", validators=[
        required(), EqualTo("new_password2", message="两次密码不匹配")
    ])
    new_password2 = PasswordField("再次输入新密码", validators=[required()])
    submit = SubmitField("提交")


class ChangeEmailForm(FlaskForm):
    """更改email表单"""

    password = PasswordField("密码", validators=[required()])
    email = StringField("新邮箱", validators=[required(), Email()])
    submit = SubmitField("提交")

    def validation_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已注册！")


class SendCodeForm(FlaskForm):
    """发送验证码"""

    username = StringField("用户名", validators=[required()])
    email = StringField("邮箱", validators=[required(), Email()])
    submit = SubmitField("提交")


class ResetPassword(FlaskForm):
    """重置密码"""

    username = StringField("用户名", validators=[required()])
    code = StringField("确认码", validators=[required()])
    password = PasswordField("新密码", validators=[required()])
    submit = SubmitField("提交")
