#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import uuid
import hashlib
import random


def hash_password(param):
    """hash密码"""

    param = str(param)
    return hashlib.md5(param.encode()).hexdigest()


def create_invitation_code():
    """邀请码生成"""

    return str(uuid.uuid1()).replace("-", "")


def send_mail():
    """发送邮件"""
    code = general_code()

    pass


def general_code():
    """生成code，重置密码"""

    code = random.randint(000000, 999999)
    return str(code)
