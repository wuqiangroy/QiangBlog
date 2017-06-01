#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""using postgresql"""

from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Permission:
    """权限"""

    FOLLOW = 0x01
    COMMENT = 0x02
    POST = 0x04
    EDIT_COMMENT = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    """角色表，包含用户权限等信息"""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    @staticmethod
    def insert_roles():
        roles = {
            "User": (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.POST, True),
            "manager": (Permission.FOLLOW |
                        Permission.COMMENT |
                        Permission.POST |
                        Permission.EDIT_COMMENT, False),
            "administrator": (0xff, False)
        }
        for i in roles:
            role = Role.query.filter_by(name=i).first()
            if role is None:
                role = Role(name=i)
            role.permissions = role[i][0]
            role.default = role[i][1]
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    """user表"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    invitation_code = db.Column(db.String, unique=True)
    code = db.Column(db.String)
    permissions = db.Column(db.Integer)
    confirmed = db.Column(db.Boolean, default=False)
    realname = db.Column(db.String, index=True)
    about_me = db.Column(db.Text())
    location = db.Column(db.String)
    register_time = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    invite_code = db.relationship("InviteCode", backref="invitecode", )

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    """文章表"""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, primary_key=True, unique=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.Column(db.Text)


class InviteCode(db.Model):
    """邀请码单设一个表"""

    __tablename__ = "invitecodes"

    id = db.Column(db.Integer, primary_key=True)
    invite_code = db.Column(db.String, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
