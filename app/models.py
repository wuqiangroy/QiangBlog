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
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import db, login_manager
from config import BaseConfig


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
        """将角色写入数据库"""

        roles = {
            "User": (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.POST, True),
            "Moderator": (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.POST |
                          Permission.EDIT_COMMENT, False),
            "Administrator": (0xff, False)
        }
        for i in roles:
            role = Role.query.filter_by(name=i).first()
            if role is None:
                role = Role(name=i)
            role.permissions = roles[i][0]
            role.default = roles[i][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role {}>".format(self.name)


class Follow(db.Model):
    """关注第三方表"""

    __tablename__ = "follows"

    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    """user表"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    invite_code = db.Column(db.String, unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    realname = db.Column(db.String, index=True)
    about_me = db.Column(db.Text())
    location = db.Column(db.String)
    QQ = db.Column(db.String)
    phone = db.Column(db.String)
    wechat = db.Column(db.String)
    weibo = db.Column(db.String)
    register_time = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    invite_codes = db.relationship("InviteCode", backref="user", lazy="dynamic")
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan'
                               )
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan'
                                )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == BaseConfig.MAIL_ADMIN:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode()).hexdigest()
        self.followed.append(Follow(followed=self))

    @staticmethod
    def add_self_follows():
        """默认自己关注自己，在关注数中减一"""

        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def follow(self, user):
        """关注"""

        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        """取消关注"""

        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        """是否关注user"""

        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed(self, user):
        """是否被user关注"""

        return self.follower.filter_by(follower_id=user.id).first() is not None

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

    def generate_confirmatiom_token(self, expiration=3600):
        """生成邮箱确认token"""

        s = Serializer(BaseConfig.SECRET_KEY, expiration)
        return s.dumps({"confirm": self.id})

    def confirm(self, token):
        """
        验证token
        token通过即将confirmed设置为True
        """

        s = Serializer(BaseConfig.SECRET_KEY)
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("confirm") != self.id:
            print(data.get("confirm"))
            print(self.id)
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        """生成重置密码所需token"""

        s = Serializer(BaseConfig.SECRET_KEY, expiration)
        return s.dumps({"reset": self.id})

    def reset_password(self, token, new_password):
        """重置密码"""

        s = Serializer(BaseConfig.SECRET_KEY)
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

    def generate_change_email_token(self, new_email, expiration=3600):
        """生成更改邮箱所需token"""

        s = Serializer(BaseConfig.SECRET_KEY, expiration)
        return s.dumps({
            "change_email": self.id,
            "new_email": new_email
        })

    def change_email(self, token):
        """验证token，更改email"""

        s = Serializer(BaseConfig.SECRET_KEY)
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

    # @staticmethod
    # def change_body(target, value, oldvalue, initiator):
    #     allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code",
    #                     "em", "i", "li", "ol", "pre", "strong", "ul",
    #                     "h1", "h2", "h3", "p"]
    #     target.text_html = bleach.linkify(bleach.clean(
    #         markdown(value, output_format="html"),
    #         tags=allowed_tags, strip=True))

# db.event.listen(Post.content, "set", Post.change_body)


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

#     @staticmethod
#     def change_body(target, value, oldvalue, initiator):
#         allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code",
#                         "em", "i", "li", "ol", "pre", "strong", "ul",
#                         "h1", "h2", "h3", "p"]
#         target.text_html = bleach.linkify(bleach.clean(
#             markdown(value, output_format="html"),
#             tags=allowed_tags, strip=True))
#
# db.event.listen(Comment.text, "set", Comment.change_body)


class InviteCode(db.Model):
    """邀请码单设一个表"""

    __tablename__ = "invitecodes"

    id = db.Column(db.Integer, primary_key=True)
    invite_code = db.Column(db.String, unique=True)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class AnonymousUser(AnonymousUserMixin):
    """匿名用户"""

    def can(self, permission):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """载入用户"""

    return User.query.get(int(user_id))
