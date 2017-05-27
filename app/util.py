#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import uuid
import hashlib
import random

from app import db
from app.models import User


def create_invitation_code():
    """邀请码生成"""

    return str(uuid.uuid1()).replace("-", "")


def send_mail():
    """发送邮件, 并将code存进User表"""
    
    code = general_code()
    user = User(
        code=code
    )
    db.session.add(user)
    db.session.commit()
    pass


def general_code():
    """生成code，重置密码"""

    code = random.randint(100000, 999999)
    return str(code)
