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
import types
from abc import ABC

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

# Works
_work = {}
auth_code = 0


class IndexHandler(RequestHandler, ABC):
    def get(self):
        self.write('''
            <b>Python MDS Server</b><br>
            To switch data in multiprocessing.<hr>
            (c)2020 <a href="https://starinc.xyz">Star Inc.</a>
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
        if isinstance(result, types.GeneratorType):
            result = {"status": 200}
        self.write(json.dumps(result))


class PythonMDS:
    switch_data = {}

    # Main
    app = Application([
        ('/', IndexHandler)
    ])
    server = HTTPServer(app)
    async_lock = IOLoop.current()

    def __init__(self):
        _work["UPT"] = self._update
        _work["DEL"] = self._delete
        _work["GET"] = self._query
        _work["SYC"] = self._sync
        _work["YLD"] = self._yuuki_limit_decrease
        _work["EXT"] = self._shutdown

    def _query(self, data):
        query_data = data["path"]
        if type(self.switch_data) is dict and type(query_data) is list:
            result = self.switch_data
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

    def _update(self, data):
        if type(data["path"]) is list:
            over = self._query({"path": data["path"]})
            over.get("data").update(data["data"])
            return {"status": 200}
        return {"status": 400}

    def _delete(self, data):
        if type(data["path"]) is list:
            over = self._query({"path": data["path"]})
            over.get("data").pop(data["data"])
            return {"status": 200}
        return {"status": 400}

    def _sync(self, data):
        self.switch_data = data["path"]
        return {"status": 200}

    def _yuuki_limit_decrease(self, data):
        self.switch_data["LimitInfo"][data["path"]][data["userId"]] -= 1
        return {"status": 200}

    def _shutdown(self, data):
        if data:
            pass
        self.server.stop()
        yield True
        self.async_lock.stop()
        self.async_lock.close()

    def mds_listen(self, code):
        global auth_code
        auth_code = code
        self.server.listen(2019)
        self.async_lock.start()
