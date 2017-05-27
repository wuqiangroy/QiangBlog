#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
与用户无关的在此处理
发文、评论
"""

from flask import Blueprint

main = Blueprint("main", __name__)

from . import views