#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, \
    SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, \
    ValidationError

from app.models import Role, User


class ProfileForm(FlaskForm):
    """个人资料页"""

    realname = StringField("姓名", validators=[Length(0, 64)])
    phone = StringField("手机号", validators=[Length(0, 11)])
    location = StringField("住址", validators=[Length(0, 64)])
    QQ = StringField("QQ号", validators=[Length(0, 11)])
    wechat = StringField("微信号", validators=[Length(0, 64)])
    weibo = StringField("微博账号", validators=[Length(0, 64)])
    about_me = TextAreaField("简介")
    submit = SubmitField("确认")

    def valid_phone(self, field):
        if not field.data.startswith("1"):
            raise ValidationError("手机号有误")


class ProfileAdminForm(FlaskForm):
    """管理员编辑资料页"""

    username = StringField("用户名", validators=[
        DataRequired(), Length(1, 64), Regexp("[A-Za-z][A-Za-z0-9_.]*$",
                                              message="用户名只能是字母、数字、点或下划线")
    ])
    email = StringField("邮箱", validators=[DataRequired(), Email(), Length(1, 64)])
    confirmed = BooleanField("邮箱是否确认")
    role = SelectField("权限选择", coerce=int)
    realname = StringField("姓名", validators=[Length(0, 64)])
    phone = StringField("手机号", validators=[Length(0, 11)])
    location = StringField("住址", validators=[Length(0, 64)])
    QQ = StringField("QQ号", validators=[Length(0, 11)])
    wechat = StringField("微信号", validators=[Length(0, 64)])
    weibo = StringField("微博账号", validators=[Length(0, 64)])
    about_me = TextAreaField("简介")
    submit = SubmitField("确认")

    def __init__(self, user, *args, **kwargs):
        super(ProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def valid_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已存在")

    def valid_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已存在")

    def valid_phone(self, field):
        if not field.data.startswith("1"):
            raise ValidationError("手机号有误")


class PostForm(FlaskForm):
    """文章"""

    title = StringField("标题", validators=[DataRequired()])
    content = TextAreaField("正文", validators=[DataRequired()])
    submit = SubmitField("发布")


class CommentForm(FlaskForm):
    """评论"""

    body = TextAreaField("", validators=[DataRequired()])
    submit = SubmitField("发布")
