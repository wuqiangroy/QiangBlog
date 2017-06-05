#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""错误页"""

from flask import render_template, request, jsonify
from . import main


@main.app_errorhandler(403)
def forbidden(e):
    """403 拒绝访问"""

    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({"error": "forbidden"})
        response.status_code = 403
        return response
    return render_template("403.html"), 403


@main.app_errorhandler(404)
def not_found(e):
    """404 页面未找到"""

    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({"error": "not_found"})
        response.status_code = 404
        return response
    return render_template("404.html"), 404


@main.app_errorhandler(5000)
def internal_server_error(e):
    """500 服务器内部错误"""

    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({"error": "internal_server_error"})
        response.status_code = 500
        return response
    return render_template("500.html"), 500
