#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=12300)
