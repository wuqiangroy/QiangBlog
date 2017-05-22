#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import uuid
import hashlib


def hash_password(param):
    """hash密码"""

    param = str(param)
    return hashlib.md5(param.encode()).hexdigest()


def create_invitation_code():
    """邀请码生成"""

    return str(uuid.uuid1()).replace("-", "")
