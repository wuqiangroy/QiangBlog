#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from app import create_app, db
from app.models import User, Post, InviteCode
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app()
manager = Manager(app)
migrate = Migrate(app)


def make_shell_context():
    """设置shell"""

    return dict(
        app=app,
        db=db,
        User=User,
        Post=Post,
        InviteCode=InviteCode
    )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
