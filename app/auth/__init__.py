#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""所有用戶方面在此處理"""

from flask import Blueprint
from . import views

auth = Blueprint("auth", __name__)
