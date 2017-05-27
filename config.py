#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    """基础配置"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "coding change world"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = ["QiangBlog"]
    MAIL_SENDER = "wuqiangroy@live.com"
    MAIL_SERVER = "smtp.live.com"
    MAIL_PORT = 587
    MAIL_USE_SSL = True
    MAIL_USERNAME = "wuqiangroy@live.com"
    MAIL_PASSWORD = os.environ.get("PASSWORD")

    @staticmethod
    def init_app(app):
        pass


class Development(Config):
    """开发配置"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://dbuser:password@localhost/dev_qiangblog"


class Production(Config):
    """线上配置"""

    SQLALCHEMY_DATABASE_URI = "postgresql://dbuser:password@localhost/pro_qiangblog"

Config = {
    "development": Development,
    "production": Production,
    "default": Development
}