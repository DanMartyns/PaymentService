from flask import request, Blueprint, session
from server import db
from server.models import Account, Active_Sessions
from server.auxiliar_functions import Message
from functools import wraps
from http import HTTPStatus
from flask import abort
import uuid
import json
import array


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):

        if 'Authorization' not in request.headers:
            abort(401)
            # It is important only abort the operation.
            # If there is a specific error message, the user will
            # know that the operation you are trying to access exists.

        auth_token = request.headers.get('Authorization')

        if auth_token:
            try:
                # For this project we will ignore the correct implementation of security
                user_id = Account.decode_auth_token(auth_token.encode())
                # data = request.headers['Authorization'].encode('ascii', 'ignore')
                # token = str.replace(str(data), 'Bearer ', '')
                # token = Account.encode_auth_token(token)
            except:
                abort(401, {'status': 'fail', 'message': user_id})
            return f(user_id, *args, **kws)
        else:
            abort(401)

    return decorated_function


# CONFIG
user_controller = Blueprint('user', __name__)


@user_controller.route('/login', methods=['POST'])
def login():
    """
        User Login Resource
    """
    code = HTTPStatus.OK
    msg = Message()

    # Get parameters
    user_id = uuid.UUID(uuid.UUID(request.json.get('user_id')).hex)
    password = request.json.get('password')

    try:
        # fetch the user data
        current_user = Account.find_by_id(user_id)

        if not current_user:
            code = HTTPStatus.NOT_FOUND
            response = {
                'status': 'fail',
                'message': 'User {} doesn\'t exist'.format(user_id)
            }

        if Account.check_password_hash(current_user.password, password):

            auth_token = Account.encode_auth_token(current_user.id)

            # mark the token into Active_Sessions
            active_session = Active_Sessions(token=auth_token)
            active_session.save_to_db()

            if auth_token:
                response = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token.decode()
                }

                return msg.message(code, response)
        else:
            code = HTTPStatus.BAD_REQUEST
            response = {
                'status': 'fail',
                'message': 'Wrong Credentials'
            }
            return msg.message(code, response)
    except Exception as e:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': str(e)
        }
        return msg.message(code, response)


@user_controller.route('/logout', methods=['POST'])
@login_required
def logout():
    """
        Logout Resource
    """
    # get auth token
    code = HTTPStatus.OK
    msg = Message()

    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = Account.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            Active_Sessions.query.filter(Active_Sessions.token == auth_token).delete()

            response = {
                'status': 'success',
                'message': 'Successfully logged out.'
            }
            return msg.message(code, response)
        else:
            code = HTTPStatus.UNAUTHORIZED
            response = {
                'status': 'fail',
                'message': resp
            }
            return msg.message(code, response)
    else:
        code = HTTPStatus.FORBIDDEN
        response = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return msg.message(code, response)
