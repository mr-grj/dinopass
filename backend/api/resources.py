import os

from flask import Blueprint, jsonify, request, make_response
from flask_restful import Api, Resource, abort

from webargs import fields, validate
from webargs.flaskparser import use_args, parser

from backend.encryption import generate_hash_key, generate_key_derivation
from backend.views import MasterPasswordView, PasswordView
from backend.models import SESSION

blueprint = Blueprint('password', __name__)
password_api = Api(blueprint)


@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    abort(error_status_code, errors=err.messages)


class MasterPassword(Resource):
    def post(self):
        """
        Create master password.

        Expected json: {'master_password': 'value_here'}
        """
        session = SESSION()
        master_password_view = MasterPasswordView(session)

        if master_password_view.has_records():
            return {
                'message': 'You have already created a master password',
                'code': 400
            }
        else:
            data = request.get_json(force=True)

            master_password = data.get('master_password')
            if not master_password:
                return {
                    'message': 'Payload should contain "master_password" key and a '
                               'non-empty value',
                    'code': 400
                }

            salt = os.urandom(16)
            hash_key = generate_hash_key(master_password)

            master_password_view.create(salt=salt, hash_key=hash_key)

            return {
                'message': 'Master password has been successfully created!',
                'status': 200
            }


class Passwords(Resource):

    @use_args({'master_password': fields.Str(required=True)}, location='query')
    def get(self, args):
        master_password = args.get('master_password')

        session = SESSION()

        master_password_view = MasterPasswordView(session)
        hash_key = generate_hash_key(master_password)
        if not master_password_view.has_records():
            return {
                'message': 'You should first create a master password',
                'code': 400
            }

        if not master_password_view.is_valid(hash_key):
            return {
                'message': 'Wrong master password',
                'code': 400
            }

        key_derivation = generate_key_derivation(master_password_view.salt, master_password)

        password_view = PasswordView(session)
        data = password_view.get_all(key_derivation)
        return jsonify(data)

    def delete(self):
        pass


class Password(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass
