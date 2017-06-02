#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
from app import create_app, db
from app.models import User, Post, InviteCode, Permission, Comment, Role,\
    Follow

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

if os.path.exists(".env"):
    print("Loading environment from .env……")
    for line in open(".env"):
        var = line.strip().split("=")
        if len(var) == 2:
            os.environ[var[0]] = var[1]

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """设置shell"""

    return dict(
        app=app,
        db=db,
        User=User,
        Post=Post,
        InviteCode=InviteCode,
        Role=Role,
        Permission=Permission,
        Comment=Comment,
        Follow=Follow
    )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
