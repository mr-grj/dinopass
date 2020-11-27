import os

from flask import Blueprint, request
from flask_restful import Api, Resource

from marshmallow import Schema, fields
from marshmallow.validate import Length

from backend.encryption import generate_hash_key
from backend.models.master_password import MasterPassword
from backend.models.user import User

users_blueprint = Blueprint('users', __name__)
users_api = Api(users_blueprint)


class CreateUserSchema(Schema):
    username = fields.Str(required=True, validate=Length(min=3, max=32))
    master_password = fields.Str(required=True, validate=Length(min=8, max=128))


class GetUserSchema(Schema):
    id_ = fields.Int(required=True)


class UsersListApi(Resource):
    def __init__(self):
        self.create_user_schema = CreateUserSchema()

    def get(self):
        users = User.query.all()
        if not users:
            return {'message': 'No users available'}, 200
        return [user.to_dict() for user in users]

    def post(self):
        data = request.get_json()
        errors = self.create_user_schema.validate(data)
        if errors:
            return {'message': errors}, 400

        username, master_password = data['username'], data['master_password']
        if User.query.filter_by(username=username).first():
            return {'message': 'Username already exists'}, 400

        master_password_model = MasterPassword.create(
            salt=os.urandom(16),
            hash_key=generate_hash_key(master_password)
        )

        User.create(
            username=username,
            master_password=master_password_model
        )

        return {'message': f'Username {username} successfully created'}, 201


class UserListApi(Resource):
    def __init__(self):
        self.get_user_schema = GetUserSchema()

    def get(self, id_):
        errors = self.get_user_schema.validate(request.view_args)
        if errors:
            return {'message': errors}, 400

        user = User.query.filter_by(id=id_).first()
        if not user:
            return {'message': f'User with id {id_} does not exist.'}, 200

        return user.to_dict()
