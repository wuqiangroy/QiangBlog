#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import current_app

from . import main


@main.route("/", methods=["get", "post"])
def index():
    pass