#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""using postgresql"""

from ..manage import db


class User(db.Model):
    """user表"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), primary_key=True, unique=True)
    email = db.Column(db.String, primary_key=True, unique=True)
    password = db.Column(db.String)
    invitation_code = db.Column(db.String, unique=True)
