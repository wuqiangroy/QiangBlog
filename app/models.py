#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""using postgresql"""

import hashlib
import bleach
from markdown import markdown
from datetime import datetime
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import JSONWebSignatureSerializer as Serializer

from app import db, login_manager
from config import Config


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
    invite_code = db.Column(db.String, unique=True)
    permissions = db.Column(db.Integer)
    confirmed = db.Column(db.Boolean, default=False)
    realname = db.Column(db.String, index=True)
    about_me = db.Column(db.Text())
    location = db.Column(db.String)
    QQ = db.Column(db.String)
    phone_number = db.Column(db.String)
    wechat = db.Column(db.String)
    weibo = db.Column(db.String)
    register_time = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    invite_codes = db.relationship("InviteCode", backref="user", lazy="dynamic")
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()

    def gravatar(self, size=100, default="identicon", rating="g"):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://www.gravatar.com/avatar"
        hash = self.avatar_hash or hashlib.md5(self.email.encode()).hexdigest()
        return "{}/{}?s={}&d={}&r={}".format(url, hash, size, default, rating)

    def generate_confirmatiom_token(self):
        """生成邮箱确认token"""

        s = Serializer(Config.SECRET_KEY)
        return s.dumps({"confirm": self.id})

    def confirm(self, token):
        """
        验证token
        token通过即将confirmed设置为True
        """

        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.load(token)
        except:
            return False
        if data.get("confime") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self):
        """生成重置密码所需token"""

        s = Serializer(Config.SECRET_KEY)
        return s.dumps({"reset": self.id})

    def reset_password(self, token, new_password):
        """重置密码"""

        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("reset") != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_change_email_token(self, new_email):
        """生成更改邮箱所需token"""

        s = Serializer(Config.SECRET_KEY)
        return s.dumps({
            "change_email": self.id,
            "new_email": new_email
        })

    def change_email(self, token):
        """验证token，更改email"""

        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("change_email") != self.id:
            return False
        new_email = data.get("new_email")
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first():
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode()).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True


class Post(db.Model):
    """文章表"""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    disable = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    @staticmethod
    def change_body(target, value, oldvalue, initiator):
        allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code",
                        "em", "i", "li", "ol", "pre", "strong", "ul",
                        "h1", "h2", "h3", "p"]
        target.text_html = bleach.linkify(bleach.clean(
            markdown(value, output_format="html"),
            tags=allowed_tags, strip=True))


class Comment(db.Model):
    """评论， 和文章是多对一关系"""

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    text_html = db.Column(db.Text)
    disable = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime(), default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    @staticmethod
    def change_body(target, value, oldvalue, initiator):
        allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code",
                        "em", "i", "li", "ol", "pre", "strong", "ul",
                        "h1", "h2", "h3", "p"]
        target.text_html = bleach.linkify(bleach.clean(
            markdown(value, output_format="html"),
            tags=allowed_tags, strip=True))


class InviteCode(db.Model):
    """邀请码单设一个表"""

    __tablename__ = "invitecodes"

    id = db.Column(db.Integer, primary_key=True)
    invite_code = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class AnonymousUser(AnonymousUserMixin):
    """匿名用户"""

    def can(self, permission):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
