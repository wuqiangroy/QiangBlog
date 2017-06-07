#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import uuid
from flask import current_app, render_template, flash, redirect, url_for, \
    abort, request
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries

from . import main
from .form import PostForm, ProfileForm, ProfileAdminForm, CommentForm
from config import BaseConfig
from app import db
from app.models import User, Permission, Post, Comment, InviteCode, Role
from app.decorator import permission_required


@main.after_app_request
def after_request(response):
    """输出查询慢的sql"""

    for query in get_debug_queries():
        if query.duration >= BaseConfig.SLOW_DB_QUERY_TIME:
            current_app.logger.warning(
                "Slow query:{}\nParameters:{}\nDuration:{}\nContext:{}".format(
                    query.statement, query.parameters, query.duration,
                    query.context
                ))
    return response


@main.route("/", methods=["GET", "POST"])
@main.route("/index", methods=["GET", "POST"])
def index():
    """主页"""

    page = request.args.get("page", 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get("show_followed", ""))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.create_time.desc()).paginate(
        page, per_page=BaseConfig.POST_PER_PAGE, error_out=False
    )
    posts = pagination.items

    return render_template("home.html", posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    """个人资料页"""

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = user.posts.order_by(Post.create_time.desc()).paginate(
        page, per_page=BaseConfig.POST_PER_PAGE, error_out=False
    )
    posts = pagination.items
    invite_codes = user.invite_codes
    return render_template("profile.html", user=user, posts=posts,
                           pagination=pagination, invite_codes=invite_codes)


@main.route("/all_users")
@login_required
@permission_required(Permission.ADMINISTER)
def all_users():
    """所有用户"""

    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.register_time.desc()).paginate(
        page, per_page=BaseConfig.USERS_PER_PAGE, error_out=False
    )
    items = [item for item in pagination.items]
    return render_template("all_users.html", endpoint="main.all_users",
                           pagination=pagination, items=items)


@main.route("/edit/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """编辑个人资料"""

    form = ProfileForm()
    if form.validate_on_submit():
        current_user.realname = form.realname.data,
        current_user.phone = form.phone.data,
        current_user.location = form.location.data,
        current_user.QQ = form.QQ.data,
        current_user.wechat = form.wechat.data,
        current_user.weibo = form.weibo.data,
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash("个人资料已更新！")
        return redirect(url_for("main.profile",
                                username=current_user.username))
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
        user.username = form.username.data
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.realname = form.realname.data
        user.phone = form.phone.data
        user.location = form.location.data
        user.QQ = form.QQ.data
        user.wechat = form.wechat.data
        user.weibo = form.weibo.data
        user.about_me = form.about_me.data
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
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user._get_current_object()
        )
        db.session.add(post)
        db.session.commit()
        flash("发布成功！")
        return redirect(url_for("main.post_page", id=post.id))
    return render_template("write_post.html", form=form)


@main.route("/post/<int:id>", methods=["GET", "POST"])
def post_page(id):
    """文章页"""

    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            text=form.body.data,
            post=post,
            author=current_user._get_current_object()
        )
        db.session.add(comment)
        db.session.commit()
        flash("评论成功！")
        return redirect(url_for("main.post_page", id=post.id))

    page = request.args.get("page", 1, type=int)
    if page == -1:
        page = (post.comments.count()-1) // \
            BaseConfig.COMMENT_PER_PAGE + 1
    pagination = post.comments.order_by(Comment.create_time.asc()).paginate(
        page, per_page=BaseConfig.COMMENT_PER_PAGE, error_out=False
    )
    comments = pagination.items
    return render_template("post_page.html", post=post, form=form,
                           comments=comments, pagination=pagination)


@main.route("/edit/post/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    """编辑文章"""

    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.content = form.content.data
        post.title = form.title.data
        db.session.add(post)
        db.session.commit()
        flash("文章更新成功")
        return redirect(url_for("main.post_page", id=post.id))
    form.title.data = post.title
    form.content.data = post.content
    return render_template("edit_post.html", form=form)


@main.route("/edit/comment/<int:id>", methods=["GET", "POST"])
@login_required
def edit_comment(id):
    """编辑评论"""

    comment = Comment.query.get_or_404(id)
    if current_user != comment.author and not \
            not current_user.can(Permission.EDIT_COMMENT):
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment.text = form.body
        db.session.add(comment)
        db.session.commit()
        flash("评论已修改!")
        return redirect(url_for("main.post_page", id=comment.post_id))
    form.body.data = comment.text
    return render_template("edit_comment.html", form=form)


@main.route("/delete/post/<int:id>")
@login_required
def delete_post(id):
    """删除文章"""

    post = Post.query.get_or_404(id)
    title = post.title
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("文章《{}》已删除".format(title))
    return redirect(url_for("main.index"))


@main.route("/delete/comment/<int:id>")
@login_required
def delete_comment(id):
    """删除评论"""

    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    if current_user != comment.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash("评论已删除")
    return redirect(url_for("main.post_page", id=post_id))


@main.route("/follow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    """关注username"""

    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("没有此用户")
        return redirect(url_for("main.index"))
    if current_user.is_following(user):
        flash("你已经关注这个用户了")
        return redirect(url_for("main.profile", username=username))
    current_user.follow(user)
    flash("成功关注{}".format(username))
    return redirect(url_for("main.profile", username=username))


@main.route("/unfollow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    """取消关注username"""

    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("没有此用户")
        return redirect(url_for("main.index"))
    if not current_user.is_following(user):
        flash("你还没有关注这个用户")
        return redirect(url_for("main.profile", username=username))
    current_user.unfollow(user)
    flash("取消关注{}成功".format(username))
    return redirect(url_for("main.profile", username=username))


@main.route("/follower/<username>")
def followers(username):
    """username的所有关注者"""

    user = User.query.filter_by(username=username).first()
    if not user:
        flash("没有此用户")
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=BaseConfig.FOLLOWER_PER_PAGE, error_out=False
    )
    follows = [
        {
            "user": item.follower,
            "timestamp": item.timestamp
         }for item in pagination.items
    ]
    return render_template("followers.html", user=user, title="关注者",
                           endpoint=".followers", pagination=pagination,
                           follows=follows)


@main.route("/followed/<username>")
def followed_by(username):
    """username关注的"""

    user = User.query.filter_by(username=username).first()
    if not user:
        flash("没有此用户")
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=BaseConfig.FOLLOWED_PER_PAGE, error_out=False
    )
    follows = [
        {
            "user": item.followed,
            "timestamp": item.timestamp
        } for item in pagination.items
    ]
    return render_template("followers.html", user=user, title="关注了",
                           endpoint=".followed_by", pagination=pagination,
                           follows=follows)


@main.route("/moderate")
@login_required
@permission_required(Permission.EDIT_COMMENT)
def moderate():
    """所有评论管理"""

    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.order_by(Comment.create_time.desc()).paginate(
        page, per_page=BaseConfig.COMMENT_PER_PAGE, error_out=False
    )
    comments = pagination.items
    return render_template("moderator.html", comments=comments,
                           pagination=pagination, page=page)


@main.route("/moderator/enable/<int:id>")
@login_required
@permission_required(Permission.EDIT_COMMENT)
def moderate_enable(id):
    """展示评论"""

    comment = Comment.query.get_or_404(id)
    comment.disable = False
    db.session.add(comment)
    db.session.commit()
    return render_template(url_for("main.moderate",
                                   page=request.args.get("page", 1, type=int)))


@main.route("/moderator/disable/<int:id>")
@login_required
@permission_required(Permission.EDIT_COMMENT)
def moderate_disable(id):
    """隐藏评论"""

    comment = Comment.query.get_or_404(id)
    comment.disable = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("main.moderate",
                            page=request.args.get("page", 1, type=int)))


@main.route("/generate/invite_code")
@login_required
def generate_invite_code():
    """生成邀请码"""

    if current_user.invite_codes.count() < 5 or \
            current_user.can(Permission.ADMINISTER):
        n = 0
        while n < 5:
            invite_code = str(uuid.uuid4()).replace("-", "")
            invite = InviteCode(
                invite_code=invite_code,
                user=current_user._get_current_object()
            )
            db.session.add(invite)
            db.session.commit()
            n += 1
        flash("5个邀请码已生成")
    else:
        flash("邀请码数量足够，请不要再生成！")
        return redirect(url_for("main.profile",
                                username=current_user.username))
    return redirect(url_for("main.profile", username=current_user.username))
