#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from flask import current_app, render_template, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from . import main
from .form import PostForm, ProfileForm, ProfileAdminForm, CommentForm
from app import db
from app.models import User, Permission, Post, Comment
from app.decorator import permission_required


@main.route("/")
@main.route("/index")
def index():
    """主页"""

    pass


@main.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    """个人资料页"""

    user = User.query.filter_by(username=username).first()
    if not user:
        flash("没有此用户！")
        return redirect(url_for("main.index"))
    return render_template("profile.html", user=user)


@main.route("/edit/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """编辑个人资料"""

    form = ProfileForm()
    if form.validate_on_submit():
        user = User(
            realname=form.realname.data,
            phone=form.phone.data,
            location=form.location.data,
            QQ=form.QQ.data,
            wechat=form.wechat.data,
            weibo=form.weibo.data,
            about_me=form.about_me.data
        )
        db.session.add(user)
        db.session.commit()
        flash("个人资料已更新！")
        return redirect(url_for("main.profile", user=current_user))
    form.realname.data = current_user.realname
    form.phone.data = current_user.phone
    form.location.data = current_user.location
    form.QQ.data = current_user.QQ
    form.wechat.data = current_user.wechat
    form.weibo.data = current_user.weibo
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)


@main.route("/edit/profile_admin/<username>", methods=["GET", "POST"])
@login_required
@permission_required(Permission.ADMINISTER)
def edit_profile_admin(username):
    """管理员编辑用户资料"""

    user = User.query.filter_by(username=username).first()
    if not user:
        flash("没有此用户")
        return redirect(url_for("main.index"))
    form = ProfileAdminForm(user=user)
    if form.validate_on_submit():
        user(
            username=form.username.data,
            email=form.email.data,
            confirmed=form.confirmed.data,
            role=form.role.data,
            realname=form.realname.data,
            phone=form.phone.data,
            location=form.location.data,
            QQ=form.QQ.data,
            wechat=form.wechat.data,
            weibo=form.weibo.data,
            about_me=form.about_me.data
        )
        db.session.add(user)
        db.session.commit()
        flash("改用户资料已更新")
        return redirect(url_for("main.profile", username=username))
    form.username.data = user.username
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.realname.data = user.realname
    form.phone.data = user.phone
    form.location.data = user.location
    form.QQ.data = user.QQ
    form.wechat.data = user.wechat
    form.weibo.data = user.weibo
    form.about_me.data = user.about_me
    return render_template("edit_profile_admin.html", form=form)


@main.route("/write-post", methods=["GET", "POST"])
@login_required
def write_post():
    """发布文章"""

    form = PostForm()
    if form.validate_on_submit():
        user = User(
            title=form.title.data,
            content=form.content.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("发布成功！")
        return redirect(url_for("main.post_page", id=user.id))
    return render_template("write_post.html", form=form)


@main.route("/post/<id>", methods=["GET", "POST"])
def post_page(id):
    """文章页"""

    post = Post.query.filter_by(id=id).first()
    if not post:
        abort(404)
        return redirect(url_for("main.index"))
    if current_user.is_is_authenticated:
        pass
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data
        )
        db.session.add(comment)
        db.session.commit()
        flash("评论成功！")
        return redirect(url_for("main.post_page", id=id))
    return render_template("post_page.html", post=post, form=form)
