#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=12300)
