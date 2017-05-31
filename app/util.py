#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import uuid
import random
import threading
from flask import current_app
from flask_mail import Message

from app import db, mail
from app.models import User
from config import Config


def create_invitation_code():
    """邀请码生成"""

    return str(uuid.uuid1()).replace("-", "")


def send_async_mail(app, msg):
    """发送异步邮件"""

    with app.app_context():
        mail.send(msg)


def send_mail(receiver):
    """发送邮件, 并将code存进User表"""

    app = current_app._get_current_object()
    code = general_code()
    user = User.filter_by(email=receiver).first()
    user.code = code
    db.session.add(user)
    db.session.commit()
    text = """
        <h3>Here is your code: {},</h3>
        <h3>Please copy and paste it in the form.</h3>    
        """.format(code)
    msg = Message(Config.MAIL_SUBJECT_PREFIX, sender=Config.MAIL_SENDER,
                  recipients=[receiver])
    msg.body = "Here is your code: {}, " \
               "Please copy and paste it in the form.".format(code)
    msg.html = text
    thr = threading.Thread(target=send_async_mail, args=[app, msg])
    thr.start()
    return thr


def general_code():
    """生成code，重置密码"""

    code = random.randint(100000, 999999)
    return str(code)
