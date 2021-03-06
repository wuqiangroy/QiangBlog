#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import Flask
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from config import Config

mail = Mail()
db = SQLAlchemy()
moment = Moment()
pagedown = PageDown()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"


def create_app(config="development"):
    """创建app"""

    app = Flask(__name__)
    app.config.from_object(Config[config])
    Config[config].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .auth import auth
    from .main import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app
