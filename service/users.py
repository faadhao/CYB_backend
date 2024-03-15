#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api, reqparse, request
from flask_cors import CORS
from datetime import datetime, timedelta

import psycopg2
import hashlib
import jwt

if __name__ == "__main__":
    from dbconf import conf
else:
    from service.dbconf import conf

app = Flask(__name__)
CORS(app)
api = Api(app)

secret_key = b'secret'

class Users(Resource):
    def post(self): # 建立帳號
        item = request.get_json()

        user_data = item['data']
        if not user_data['account'] or len(user_data['account']) == 0: return make_response(jsonify({"msg": "帳號未填"}), 400)
        if not user_data['password'] or len(user_data['password']) == 0: return make_response(jsonify({"msg": "密碼未填"}), 400)
        if len(user_data['password']) > 14 or len(user_data['password']) < 6: return make_response(jsonify({"msg": "密碼需介於 6-14 字"}), 400)
        if not user_data['userName']: return make_response(jsonify({"msg": "使用者名稱未填"}), 400)

        password = hashlib.md5(user_data['password'].encode('utf-8'))

        data = [user_data['account'],password.hexdigest(),user_data['userName'],user_data['role'],user_data['gender'],'1']

        code, msg = UserService().create(data)

        return make_response(jsonify({"msg": ["建立成功", [msg, "註冊失敗"][not msg]][code == 400]}), code)
    def get(self): # 取得使用者資訊
        print('TODO')
    def put(self): # 修改使用者資訊
        item = request.get_json()

        token = item['token']
        if not token: return make_response(jsonify({"msg": "未登入"}), 401)

        valid = UserService().check_login(token)

        user_data = item['data']
        if not user_data['password'] or len(user_data['password']) == 0: return make_response(jsonify({"msg": "密碼未填"}), 400)
        if len(user_data['password']) > 14 or len(user_data['password']) < 6: return make_response(jsonify({"msg": "密碼需介於 6-14 字"}), 400)
        if not user_data['userName']: return make_response(jsonify({"msg": "使用者名稱未填"}), 400)

        password = hashlib.md5(user_data['password'].encode('utf-8'))

        data = [password.hexdigest(), user_data['userName'],user_data['gender'],[user_data['MessageAble'], '1'][not user_data['MessageAble'] or user_data['MessageAble'] == ""]]
        print('TODO')

class Login(Resource):
    def post(self): # 登入
        item = request.get_json()

        login_data = item['data']
        if not login_data['account']: return make_response(jsonify({"msg": "帳號未填"}), 400)
        if not login_data['password']: return make_response(jsonify({"msg": "密碼未填"}), 400)

        password = hashlib.md5(login_data['password'].encode('utf-8'))

        user, code = UserService().getUser([login_data['account'], password.hexdigest()])
        if len(user) == 0: return make_response(jsonify({"msg": "帳號或密碼錯誤"}), 400)
        user = user[0]
        if user[4] == "" or not user[4]:
            exp = datetime.now() + timedelta(days=1)
            data = {
                "UserID": user[0],
                "UserName": user[1],
                "UserRole": user[2],
                "MessageAble": user[3],
                "exp": exp
            }
            token = jwt.encode(payload=data, key=secret_key, algorithm='HS256')
            user_token, code = UserService().update_token(token, user[0])
            if code == 200: msg = jsonify({"msg": "登入成功", "token": user_token})
            else: msg = jsonify({"msg": "登入失敗"})
        else:
            data = jwt.decode(user[4], key=secret_key, algorithms=['HS256', ])
            exp = datetime.utcfromtimestamp(data['exp'])
            if exp < datetime.now():
                exp = datetime.now()
                data['exp'] = exp
                token = jwt.encode(payload=data, key=secret_key, algorithm='HS256')
                user_token, code = UserService().update_token(token, user[0])
            else: user_token, code = (user[4], 200)
            msg = jsonify({"msg": "登入成功", "token": user_token})

        return make_response(msg, code)

class UserService():
    def create(self, data):
        conn = psycopg2.connect(database=conf["maindb"], user=conf["user"], password=conf["pw"], host=conf["host"], port="5432")
        code = 400
        msg = None

        with conn.cursor() as cur:
            sql = """
                INSERT INTO users (UserAccount,UserPassword,UserName,UserRole,UserGender,MessageAble)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            try:
                cur.execute(sql, data)
                conn.commit()
                code = 200
            except Exception as e:
                print('error:',e)
                if type(e) == psycopg2.errors.UniqueViolation: msg = '帳號重複'

        return code, msg

    def update(self, data):
        conn = psycopg2.connect(database=conf["maindb"], user=conf["user"], password=conf["pw"], host=conf["host"], port="5432")
        code = 400
        msg = None

        with conn.cursor() as cur:
            sql = """
                UPDATE users SET Token=%s WHERE UserId=%s
            """

            try:
                cur.execute(sql, data)
                conn.commit()
                code = 200
            except Exception as e:
                print('error:',e)
                if type(e) == psycopg2.errors.UniqueViolation: msg = '帳號重複'

        return code, msg

    def getUser(self, data):
        conn = psycopg2.connect(database=conf["maindb"], user=conf["user"], password=conf["pw"], host=conf["host"], port="5432")
        code = 400

        with conn.cursor() as cur:
            sql = """
                SELECT UserID, UserName, UserRole, MessageAble, Token From users
                WHERE UserAccount=%s AND UserPassword=%s
            """

            try:
                cur.execute(sql, data)
                res = cur.fetchall()
                code = 200
            except Exception as e:
                print('error:',e)

        return res, code

    def update_token(self, token, UserId):
        conn = psycopg2.connect(database=conf["maindb"], user=conf["user"], password=conf["pw"], host=conf["host"], port="5432")
        code = 400

        with conn.cursor() as cur:
            sql = """
                UPDATE users SET Token=%s WHERE UserId=%s
            """

            try:
                cur.execute(sql, (token, UserId))
                conn.commit()
                code = 200
            except Exception as e:
                print('error:',e)

        return token, code

    def check_login(self, token):
        user = jwt.decode(user[4], key=secret_key, algorithms=['HS256', ])
        conn = psycopg2.connect(database=conf["maindb"], user=conf["user"], password=conf["pw"], host=conf["host"], port="5432")
        code = 400

        with conn.cursor() as cur:
            sql = """
                SELECT Token From users
                WHERE UserAccount=%s AND UserPassword=%s
            """

            try:
                cur.execute(sql, data)
                res = cur.fetchall()
                code = 200
            except Exception as e:
                print('error:',e)

        return res, code
