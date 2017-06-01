#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import Regexp, DataRequired, Length, Email, EqualTo
from wtforms import ValidationError

from app.models import User


class LoginForm(FlaskForm):
    """登录表单"""

    username = StringField("用户名", validators=[
        DataRequired(), Length(1, 64), Regexp("[A-Za-z][A-Za-z0-9_.]*$",
                                              message="用户名只能是字母、数字、点或下划线")
    ])
    password = PasswordField("密碼", validators=[DataRequired()])
    remember_me = BooleanField("记住我")
    submit = SubmitField("登录")


class RegisterForm(FlaskForm):
    """注冊表单"""

    username = StringField("用户名", validators=[
        DataRequired(), Length(1, 64), Regexp("[A-Za-z][A-Za-z0-9_.]*$",
                                              message="用户名只能是字母、数字、点或下划线")
    ])
    email = StringField("邮箱", validators=[DataRequired(), Email(),
                                          Length(1, 64)])
    invite_code = StringField("请输入邀请码", validators=[DataRequired()])
    password = PasswordField("密码", validators=[
        DataRequired(), EqualTo("password2", message="两次密码不正确")
    ])
    password2 = PasswordField("再次输入密码", validators=[DataRequired()])
    submit = SubmitField("提交")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已被占用！")

    def validation_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已注册！")


class ChangePasswordForm(FlaskForm):
    """更改密码表单"""

    password = PasswordField("原始密码", validators=[DataRequired()])
    new_password = PasswordField("新密码", validators=[
        DataRequired(), EqualTo("new_password2", message="两次密码不匹配")
    ])
    new_password2 = PasswordField("再次输入新密码", validators=[DataRequired()])
    submit = SubmitField("提交")


class ChangeEmailForm(FlaskForm):
    """更改email表单"""

    password = PasswordField("密码", validators=[DataRequired()])
    email = StringField("新邮箱", validators=[DataRequired(), Email(),
                                           Length(1, 64)])
    submit = SubmitField("提交")

    def validation_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已注册！")


class SendCodeForm(FlaskForm):
    """发送验证码"""

    username = StringField("用户名", validators=[
        DataRequired(), Length(1, 64), Regexp("[A-Za-z][A-Za-z0-9_.]*$",
                                              message="用户名只能是字母、数字、点或下划线")
    ])
    email = StringField("邮箱", validators=[DataRequired(), Email()])
    submit = SubmitField("提交")


class ResetPassword(FlaskForm):
    """重置密码"""

    username = StringField("用户名", validators=[
        DataRequired(), Length(1, 64), Regexp("[A-Za-z][A-Za-z0-9_.]*$",
                                              message="用户名只能是字母、数字、点或下划线")
    ])
    code = StringField("确认码", validators=[DataRequired()])
    password = PasswordField("新密码", validators=[DataRequired()])
    submit = SubmitField("提交")
