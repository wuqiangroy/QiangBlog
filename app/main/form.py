#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask_wtf import FlaskForm
from wtforms import StringField, TextField
from wtforms.validators import DataRequired


class ProfileForm(FlaskForm):
    """个人资料页"""