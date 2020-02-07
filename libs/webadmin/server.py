# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import hashlib
import json
import random
import time

from flask import Flask, render_template, Response, request, redirect
from flask_bootstrap import Bootstrap
from gevent.pywsgi import WSGIServer

from .api import Yuuki_WebAdminAPI

wa_app = Flask(__name__)
Yuuki_Handle = None
Yuuki_APIHandle = None

passports = []
password = str(hash(random.random()))


class Yuuki_WebAdmin:
    def __init__(self, Yuuki):
        global Yuuki_Handle, Yuuki_APIHandle
        Yuuki_Handle = Yuuki
        Yuuki_APIHandle = Yuuki_WebAdminAPI(Yuuki_Handle.data)

        self.app = wa_app
        Bootstrap(self.app)

    @staticmethod
    @wa_app.route("/")
    def index():
        if "yuuki_admin" in request.cookies:
            if request.cookies["yuuki_admin"] in passports:
                return render_template(
                    'manage/index.html',
                    version=Yuuki_Handle.YuukiConfigs["version"],
                    LINE_Media_server=Yuuki_Handle.LINE_Media_server,
                    profileName=Yuuki_Handle.profile.displayName,
                    pictureStatus=Yuuki_Handle.profile.pictureStatus
                )
            else:
                response = redirect("/")
                response.set_cookie(
                    key='yuuki_admin',
                    value='',
                    expires=0
                )
                return response
        else:
            return render_template(
                'index.html',
                name=Yuuki_Handle.YuukiConfigs["name"],
                version=Yuuki_Handle.YuukiConfigs["version"]
            )

    @staticmethod
    @wa_app.route("/groups")
    def groups():
        if "yuuki_admin" in request.cookies:
            if request.cookies["yuuki_admin"] in passports:
                return render_template(
                    'manage/groups.html'
                )
        response = redirect("/")
        response.set_cookie(
            key='yuuki_admin',
            value='',
            expires=0
        )
        return response

    @staticmethod
    @wa_app.route("/helpers")
    def helpers():
        if "yuuki_admin" in request.cookies:
            if request.cookies["yuuki_admin"] in passports:
                return render_template(
                    'manage/groups.html'
                )
        response = redirect("/")
        response.set_cookie(
            key='yuuki_admin',
            value='',
            expires=0
        )
        return response

    @staticmethod
    @wa_app.route("/settings")
    def settings():
        if "yuuki_admin" in request.cookies:
            if request.cookies["yuuki_admin"] in passports:
                return render_template(
                    'manage/settings.html'
                )
        response = redirect("/")
        response.set_cookie(
            key='yuuki_admin',
            value='',
            expires=0
        )
        return response

    @staticmethod
    @wa_app.route("/verify", methods=['GET', 'POST'])
    def verify():
        result = {"status": 403}
        if request.method == "POST" and "code" in request.values:
            if request.values["code"] == password:
                seed = hash(random.random() + time.time())
                seed = str(seed).encode('utf-8')
                session_key = hashlib.sha256(seed).hexdigest()
                passports.append(session_key)
                result = {"status": 200, "session": session_key}
            else:
                result = {"status": 401}
        return Response(json.dumps(result), mimetype='application/json')

    @staticmethod
    @wa_app.route("/logout")
    def logout():
        response = redirect("/")
        if "yuuki_admin" in request.cookies:
            if request.cookies.get("yuuki_admin") in passports:
                passports.remove(request.cookies.get("yuuki_admin"))
            response.set_cookie(
                key='yuuki_admin',
                value='',
                expires=0
            )
        return response

    @staticmethod
    @wa_app.route("/events")
    def events():
        if "yuuki_admin" in request.cookies:
            if request.cookies["yuuki_admin"] in passports:
                return render_template(
                    'manage/events.html'
                )
        response = redirect("/")
        response.set_cookie(
            key='yuuki_admin',
            value='',
            expires=0
        )
        return response

    @staticmethod
    @wa_app.route("/api", methods=['GET', 'POST'])
    def api():
        result = {"status": 403}
        if request.method == "POST" and "task" in request.values:
            if request.cookies.get("yuuki_admin") in passports:
                query_result = Yuuki_APIHandle.init(request.values)
                result = {"status": 200, "result": query_result}
            else:
                result = {"status": 401}
        return Response(json.dumps(result), mimetype='application/json')

    @staticmethod
    @wa_app.route("/api/i")
    def i():
        return Yuuki_Handle.YuukiConfigs["name"]

    @staticmethod
    def set_password(code):
        global password
        password = code

    def start(self, admin_password):
        self.set_password(admin_password)
        http_server = WSGIServer(('', 2020), self.app)
        http_server.serve_forever()
