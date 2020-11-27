from flask import Blueprint, request
from flask_restful import Api, Resource

from marshmallow import Schema, fields
from marshmallow.validate import Length

from backend.models.master_password import MasterPassword
from backend.models.password import Password

passwords_blueprint = Blueprint('passwords', __name__)
passwords_api = Api(passwords_blueprint)


class CreatePasswordSchema(Schema):
    user_id = fields.Int(required=True)
    master_password = fields.Str(required=True, validate=Length(min=3, max=64))
    password_name = fields.Str(required=True, validate=Length(min=3, max=64))
    password_value = fields.Str(required=True, validate=Length(min=1, max=128))


class GetPasswordsSchema(Schema):
    user_id = fields.Int(required=True)
    master_password = fields.Str(required=True, validate=Length(min=3, max=64))


class PasswordsListApi(Resource):
    def __init__(self):
        self.create_password_schema = CreatePasswordSchema()
        self.get_passwords_schema = GetPasswordsSchema()

    def post(self):
        data = request.get_json()
        errors = self.create_password_schema.validate(data)
        if errors:
            return {'message': errors}, 400

        user_id, password_name, password_value = data['user_id'], data['password_name'], data['password_value']
        master_password = data['master_password']

        if not MasterPassword.is_valid(user_id, master_password):
            return {'message': 'Invalid master password'}, 400

        if Password.query.filter_by(user_id=user_id, name=password_name).first():
            return {'message': 'A password with this name already exists'}, 400

        Password.create(
            user_id=user_id,
            name=password_name,
            value=password_value
        )

        return {'message': f'Password {password_name} successfully created'}, 201
