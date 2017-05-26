#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from .auth import auth

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth)

    return app
