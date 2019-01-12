# _*_ coding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse
from models import User, UserSchema

parser = reqparse.RequestParser()
help_text = "This field cannot be blank"
parser = parser.add_argument("first_name",help=help_text,required=True)
parser = parser.add_argument("last_name",help=help_text,required=True)
parser = parser.add_argument("email",help=help_text,required=True)
parser = parser.add_argument("password",help=help_text,required=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class UserRegister(Resource):
    # register with code in a link
    def post(self):
        data = parser.parse_args()

        user = User.find_by_email(data.get("email"))
        if user:
            return {"message": "User {0} already exists".format(
                data.get("email"))}
        try:
            user = User.create_user(data)
            user.is_admin = False
            user.save_to_db()
            message = "User {0} was created".format(data.get("first_name"))
            return {"message": message}
        except:
            return {"message":"Something went wrong"},500


class UserLogin(Resource):
    def post(self):
        args = parser.parse_args()

        user = User.find_by_email(data.get("email"))
        if not user:
            return {"message": "User {0} doesn\'t exist".format(
                data.get("email"))}

        if User.verify_hash(data.get("password"),user.password):
            user = user_schema.dumps(user).data()
            return {"message": "Logged in as {0}".format(data.get("email")),
                    "data":user}
        else:
            return {"message": "Wrong credentials"}

        return {"message": "User login"}



class UserLogoutAcess(Resource):
    def post(self):
        return {"message": "User logout"}

class UserLogoutRefresh(Resource):
    def post(self):
        return {"message": "User logout"}

class TokenRefresh(Resource):
    def post(self):
        return {"message": "Token refresh"}

class UserResource(Resource):
    def get(self):
        users = User.get_all_users()
        users = users_schema.dump(users).data
        return {'status':'success','data':users},200

    def delete(self):
        return {"message": "Delete user"}

class SecretResource(Resource):
    def get(self):
        return {
            "answer": 43
        }
