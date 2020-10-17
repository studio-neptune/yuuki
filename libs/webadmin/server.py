# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import hashlib
import random
import time

from flask import Flask, render_template, request, redirect, jsonify
from flask_bootstrap import Bootstrap
from gevent.pywsgi import WSGIServer
from functools import wraps

from .reader import Yuuki_WebDataReader
from ..tools import Yuuki_DynamicTools

wa_app = Flask(__name__)

Yuuki_Handle = None
Yuuki_Handle_Data = None
Yuuki_APIHandle_Data = None

passports = []
password = str(hash(random.random()))


def authorized_response(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "yuuki_admin" in request.cookies \
                and request.cookies["yuuki_admin"] in passports:
            return jsonify(function(*args, **kwargs))
        response = jsonify({"status": 403})
        response.set_cookie(
            key='yuuki_admin',
            value='',
            expires=0
        )
        return response
    return wrapper


class Yuuki_WebAdmin:
    Bootstrap(wa_app)
    http_server = None

    def __init__(self, Yuuki):
        global Yuuki_Handle, Yuuki_Handle_Data, Yuuki_APIHandle_Data
        Yuuki_Handle = Yuuki
        Yuuki_Handle_Data = Yuuki.data
        Yuuki_APIHandle_Data = Yuuki_WebDataReader(Yuuki_Handle_Data)

    @staticmethod
    def set_password(code):
        global password
        password = code

    def wa_listen(self):
        self.http_server = WSGIServer(('', 2020), wa_app)
        self.http_server.serve_forever()

    # HTML Server
    @staticmethod
    @wa_app.route("/")
    def index():
        status = False
        if "yuuki_admin" in request.cookies \
                and request.cookies["yuuki_admin"] in passports:
            status = True
        return render_template(
            '/index.html',
            name=Yuuki_Handle.YuukiConfigs["name"],
            authorized=status
        )

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

    # API Points
    @staticmethod
    @wa_app.route("/api/verify", methods=['POST'])
    def verify():
        if "code" in request.values:
            if request.values["code"] == password:
                seed = hash(random.random() + time.time())
                seed = str(seed).encode('utf-8')
                session_key = hashlib.sha256(seed).hexdigest()
                passports.append(session_key)
                result = jsonify({"status": 200, "session": session_key})
                result.set_cookie(
                    key='yuuki_admin',
                    value=session_key
                )
                return result
            return jsonify({"status": 401})
        return jsonify({"status": 403})

    @staticmethod
    @wa_app.route("/api/profile", methods=["GET", "PUT"])
    @authorized_response
    def profile():
        if request.method == "GET":
            return {
                "version": Yuuki_Handle.YuukiConfigs["version"],
                "name": Yuuki_Handle.profile.displayName,
                "status": Yuuki_Handle.profile.statusMessage,
                "picture": f"{Yuuki_Handle.LINE_Media_server}/{Yuuki_Handle.profile.pictureStatus}"
            }
        if request.method == "PUT" and "name" in request.values and "status" in request.values:
            Yuuki_Handle.profile.displayName = request.values["name"]
            Yuuki_Handle.profile.statusMessage = request.values["status"]
            Yuuki_DynamicTools(Yuuki_Handle).getClient(Yuuki_Handle.MyMID).updateProfile(
                Yuuki_Handle.Seq, Yuuki_Handle.profile
            )
            return {"status": 200}
        return {"status": 400}

    @staticmethod
    @wa_app.route("/api/groups", methods=["GET", "POST", "DELETE"])
    @authorized_response
    def groups():
        if request.method == "GET":
            return Yuuki_Handle_Data.getData(["Global", "GroupJoined"])
        if request.method == "POST" and "id" in request.values:
            return Yuuki_DynamicTools(Yuuki_Handle).getClient(Yuuki_Handle.MyMID).acceptGroupInvitation(
                Yuuki_Handle.Seq, request.values["id"]
            )
        if request.method == "DELETE" and "id" in request.values:
            return Yuuki_DynamicTools(Yuuki_Handle).getClient(Yuuki_Handle.MyMID).leaveGroup(
                Yuuki_Handle.Seq, request.values["id"]
            )
        return {"status": 400}

    @staticmethod
    @wa_app.route("/api/group/ticket", methods=["POST"])
    @authorized_response
    def group_ticket():
        if "id" in request.values and "ticket" in request.values:
            return Yuuki_DynamicTools(Yuuki_Handle).getClient(Yuuki_Handle.MyMID).acceptGroupInvitationByTicket(
                Yuuki_Handle.Seq, request.values["id"], request.values["ticket"]
            )
        return {"status": 400}

    @staticmethod
    @wa_app.route("/api/groups/<id_list>")
    @authorized_response
    def groups_information(id_list=None):
        read_id_list = id_list.split(",")
        if isinstance(read_id_list, list) and len(read_id_list) > 0:
            def type_handle(obj):
                for key in obj.__dict__:
                    if key == "pictureStatus" and obj.__dict__[key] is not None:
                        obj.__dict__[
                            key] = f"{Yuuki_Handle.LINE_Media_server}/{obj.__dict__[key]}"
                    if isinstance(obj.__dict__[key], list):
                        obj.__dict__[key] = list(
                            map(type_handle, obj.__dict__[key]))
                    if hasattr(obj.__dict__[key], '__dict__'):
                        obj.__dict__[key] = obj.__dict__[key].__dict__
                return obj.__dict__
            return list(map(type_handle, Yuuki_DynamicTools(Yuuki_Handle).getClient(Yuuki_Handle.MyMID).getGroups(read_id_list)))
        return {"status": 400}

    @staticmethod
    @wa_app.route("/api/helpers")
    @authorized_response
    def helpers():
        return Yuuki_Handle.Connect.helper

    @staticmethod
    @wa_app.route("/api/settings")
    @authorized_response
    def settings():
        return None

    @staticmethod
    @wa_app.route("/api/events/<doctype>")
    @authorized_response
    def get_logs(doctype):
        return Yuuki_APIHandle_Data.get_logs(doctype)

    @staticmethod
    @wa_app.route("/api/broadcast", methods=["POST"])
    @authorized_response
    def broadcast():
        if "message" in request.values and "audience" in request.values and request.values["message"]:
            audience_ids = {
                "groups": lambda: Yuuki_Handle_Data.getData(
                    ["Global", "GroupJoined"]
                )
            }
            if request.values["audience"] not in audience_ids:
                return {"status": "404"}
            return list(map(
                lambda target_id: Yuuki_DynamicTools(Yuuki_Handle).sendText(
                    target_id, request.values["message"]
                ),
                audience_ids[request.values["audience"]]()
            ))
        return {"status": 400}

    @staticmethod
    @wa_app.route("/api/shutdown")
    @authorized_response
    def shutdown():
        LINE_ACCOUNT_SECURITY_NOTIFY_ID = "u085311ecd9e3e3d74ae4c9f5437cbcb5"
        # The ID belongs to an official account, which is controlled by SysOp of LINE.
        Yuuki_DynamicTools(Yuuki_Handle).sendText(
            LINE_ACCOUNT_SECURITY_NOTIFY_ID,
            "[Yuuki] Remote Shutdown"
        )
        return {"status": 200}
