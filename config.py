#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """基础配置"""

    SECRET_KEY = os.environ.get("secret_key") or "coding change world"
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5
    MAIL_SUBJECT_PREFIX = "[QiangBlog]"
    MAIL_SENDER = "QiangBlog <wuqiangroy@yeah.net>"
    MAIL_SERVER = "smtp.yeah.net"
    MAIL_USE_SSL = True
    MAIL_USERNAME = "wuqiangroy@yeah.net"
    MAIL_PASSWORD = os.environ.get("password")
    MAIL_ADMIN = os.environ.get("MAIL_ADMIN") or "wuqiangroy@live.com"
    POST_PER_PAGE = 20
    COMMENT_PER_PAGE = 20
    FOLLOWER_PER_PAGE = 20
    FOLLOWED_PER_PAGE = 20
    BOOTSTRAP_SERVE_LOCAL = True

    @staticmethod
    def init_app(app):
        pass


class Development(BaseConfig):
    """开发配置"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://dbuser:password@localhost/dev_qiangblog"


class Production(BaseConfig):
    """线上配置"""

    SQLALCHEMY_DATABASE_URI = "postgresql://dbuser:password@localhost/pro_qiangblog"

Config = {
    "development": Development,
    "production": Production,
    "default": Development
}
