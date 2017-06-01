#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""权限装饰器"""

from functools import wraps
from flask import abort
from flask_login import current_user

from .models import Permission


def permission_required(permission):
    """需要权限，传入所需权限参数"""

    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorator_function
    return decorator


def admin_required():
    """管理员所需权限"""
    return permission_required(Permission.ADMINISTER)

