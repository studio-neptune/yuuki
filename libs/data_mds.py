#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Star Inc. multiprocessing data switching
    ===
        To switch data in multiprocessing.

    LICENSE: MPL 2.0
                               (c)2019 Star Inc.
"""

# Initializing
import json

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

switch_data = {}
auth_code = 0

# Functions
def mds_exit(null=None, null_=None):
    exit(0)

def update(path, data):
    global switch_data
    try:
        if type(path) is list:
            over = query(path)
            over.get("data").update(data)
            return {"status" : 200}
        return {"status" : 400}
    except:
        return {"status": 500}

def delete(path, data):
    global switch_data
    try:
        if type(path) is list:
            over = query(path)
            over.get("data").pop(data)
            return {"status" : 200}
        return {"status" : 400}
    except:
        return {"status": 500}

def query(query_data, null=None):
    global switch_data
    try:
        if type(switch_data) is dict and type(query_data) is list:
            result = switch_data
            query_len = len(query_data)
            source_data = switch_data
            for count, key in enumerate(query_data):
                if key in source_data:
                    if count < (query_len -  1):
                        if type(source_data.get(key)) is dict:
                            source_data = source_data.get(key)
                        else:
                            result = 1 #"unknown_type" + type(source_data.get(key))
                            break
                    else:
                        result = source_data.get(key)
                else:
                    result = 2 #"unknown_key"
                    break

            return {"status" : 200, "data" : result}
        return {"status" : 400}
    except:
        return {"status": 500}

def sync(path, null=None):
    global switch_data
    try:
        switch_data = path
        return {"status" : 200}
    except:
        return {"status": 500}

def yuukiLimitDecrease(path, userId):
    global switch_data
    try:
        switch_data["LimitInfo"][path][userId] -= 1
        return {"status" : 200}
    except:
        return {"status": 500}

# Works
_work = {
    "EXT": mds_exit,
    "UPT": update,
    "DEL": delete,
    "GET": query,
    "SYC": sync,
    "YLD": yuukiLimitDecrease
}

class IndexHandler(RequestHandler):
    def get(self):
        self.write('''
            <b>Python MDS Server</b><br>
            To switch data in multiprocessing.<hr>
            (c)2019 <a href="https://starinc.xyz">Star Inc.</a>
        ''')

    def post(self):
        global auth_code
        req_body = self.request.body
        req_str = req_body.decode('utf8')
        req_res = json.loads(req_str)
        if req_res.get("code") == auth_code:
            result = _work[req_res.get("do")](req_res.get("path"), req_res.get("data"))
        else:
            result = {"status" : 401}
        if not result:
            result = {"status" : 500}
        self.write(json.dumps(result))

# Main
def listen(code):
    global auth_code
    auth_code = code
    app = Application([('/',IndexHandler)])
    server = HTTPServer(app)
    server.listen(2019)
    IOLoop.current().start()
