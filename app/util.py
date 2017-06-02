#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import uuid
import threading
from flask import current_app, render_template
from flask_mail import Message

from app import mail
from config import BaseConfig


def create_invitation_code():
    """邀请码生成"""

    return str(uuid.uuid1()).replace("-", "")


def send_async_mail(app, msg):
    """发送异步邮件"""

    with app.app_context():
        mail.send(msg)


def send_mail(receiver, subject, template, **kwargs):
    """发送邮件"""

    app = current_app._get_current_object()
    msg = Message(BaseConfig.MAIL_SUBJECT_PREFIX + "" + subject,
                  sender=BaseConfig.MAIL_SENDER, recipients=[receiver])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr = threading.Thread(target=send_async_mail, args=[app, msg])
    thr.start()
    return thr
