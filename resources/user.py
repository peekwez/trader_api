# _*_ coding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse
from functools import wraps

from extensions import jwt
from models import User, TokenBlackList
from serializers import UserSchema
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt, get_jwt_claims)
from datetime import datetime

help_text = "This field cannot be blank"
rg_parser = reqparse.RequestParser()
rg_parser.add_argument("first_name",help=help_text,required=True)
rg_parser.add_argument("last_name",help=help_text,required=True)
rg_parser.add_argument("email",help=help_text,required=True)
rg_parser.add_argument("password",help=help_text,required=True)

lg_parser = reqparse.RequestParser()
lg_parser.add_argument("email",help=help_text,required=True)
lg_parser.add_argument("password",help=help_text,required=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

def admin_rights_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        is_admin = get_jwt_claims()
        if is_admin:
            return func(*args,**kwargs)
        else:
            return {
                "message": "Access Denied"
            },401
    return wrapper


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {"is_admin": user.is_admin}


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.email


class UserRegister(Resource):
    # register with code in a link
    def post(self):
        data = rg_parser.parse_args()

        user = User.find_by_email(data.get("email"))
        if user:
            return {"message": "User {0} already exists".format(
                data.get("email"))}

        user = User.create_user(data)
        try:
            user.is_admin = False
            user.last_login = datetime.now()
            user.date_joined = user.last_login
            user.save_to_db()

            # create tokens
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)

            # add tokens to db
            TokenBlackList.add_token(access_token)
            TokenBlackList.add_token(refresh_token)

            return {
                "access_token":access_token,
                "refresh_token":refresh_token
            },201
        except:
            return {"message":"Something went wrong"},500


class UserLogin(Resource):
    def post(self):
        data = lg_parser.parse_args()

        user = User.find_by_email(data.get("email"))
        if not user:
            return {"message": "User {0} doesn\'t exist".format(
                data.get("email"))}

        if User.verify_hash(data.get("password"),user.password):

            # update last login
            user.update_last_login()

            # get tokens
            access_token  = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)

            # add tokens to db
            TokenBlackList.add_token(access_token)
            TokenBlackList.add_token(refresh_token)

            return {
                "access_token":access_token,
                "refresh_token":refresh_token
            }
        else:
            return {"message": "Wrong credentials"}

        return {"message": "User login"}



class UserLogoutAccess(Resource):

    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        try:
            TokenBlackList.revoke_token(jti)
            return {"message": "Access token has been revoked"}
        except:
            return {"message": "Something went wrong"}, 500

class UserLogoutRefresh(Resource):

    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        try:
            TokenBlackList.revoke_token(jti)
            return {"message": "Refresh token has been revoked"}
        except:
            return {"message": "Something went wrong"}, 500


class TokenRefresh(Resource):

    @jwt_refresh_token_required
    def post(self):
        user = User.find_by_email(get_jwt_identity())
        access_token = create_access_token(identity=user)
        return {"access_token": access_token}


class UserResource(Resource):

    @admin_rights_required
    @jwt_required
    def get(self):
        users = User.get_all_users()
        users = users_schema.dump(users).data
        return {'data':users},200

    @admin_rights_required
    @jwt_required
    def delete(self,ids):
        User.delete_users(ids)
        return {"message": "Users deleted"}

class SecretResource(Resource):

    @jwt_required
    def get(self):
        return {
            "answer": 43
        }
