# -*- coding: utf-8 -*-
"""
    Star Inc. multiprocessing data switching
    ===
        To switch data in multiprocessing.

    LICENSE: MPL 2.0
                               (c)2020 Star Inc.
"""

# Initializing
import json

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

switch_data = {}
auth_code = 0


# Functions
def update(data):
    global switch_data
    # noinspection PyBroadException
    try:
        if type(data["path"]) is list:
            over = query({"path": data["path"]})
            over.get("data").update(data["data"])
            return {"status": 200}
        return {"status": 400}
    except:
        return {"status": 500}


def delete(data):
    global switch_data
    # noinspection PyBroadException
    try:
        if type(data["path"]) is list:
            over = query({"path": data["path"]})
            over.get("data").pop(data["data"])
            return {"status": 200}
        return {"status": 400}
    except:
        return {"status": 500}


def query(data):
    global switch_data
    query_data = data["path"]
    # noinspection PyBroadException
    try:
        if type(switch_data) is dict and type(query_data) is list:
            result = switch_data
            query_len = len(query_data) - 1
            for count, key in enumerate(query_data):
                if key in result:
                    if count < query_len:
                        if type(result.get(key)) is not dict:
                            result = 1  # "unknown_type" + type(source_data.get(key))
                            break
                    result = result.get(key)
                else:
                    result = 2  # "unknown_key"
                    break

            return {"status": 200, "data": result}
        return {"status": 400}
    except:
        return {"status": 500}


def sync(data):
    global switch_data
    # noinspection PyBroadException
    try:
        switch_data = data["path"]
        return {"status": 200}
    except:
        return {"status": 500}


def yuukiLimitDecrease(data):
    global switch_data
    # noinspection PyBroadException
    try:
        switch_data["LimitInfo"][data["path"]][data["userId"]] -= 1
        return {"status": 200}
    except:
        return {"status": 500}


# Works
_work = {
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
            result = _work[req_res.get("do")](
                {
                    "path": req_res.get("path"),
                    "data": req_res.get("data")
                }
            )
        else:
            result = {"status": 401}
        if not result:
            result = {"status": 500}
        self.write(json.dumps(result))


# Main
app = Application([
    ('/', IndexHandler)
])
server = HTTPServer(app)
async_lock = IOLoop.current()


def listen(code):
    global auth_code
    auth_code = code
    server.listen(2019)
    async_lock.start()


def mds_exit():
    server.stop()
    yield server.close_all_connections()
    async_lock.stop()
    async_lock.close()
