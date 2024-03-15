#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, request, make_response
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS

from service.users import Users, Login

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(Users,'/users')
api.add_resource(Login,'/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3300, debug=True, threaded=True)