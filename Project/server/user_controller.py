from flask import request, Blueprint, session
from server import db
from server.models import Account, Active_Sessions
from server.auxiliar_functions import Message
from functools import wraps
from http import HTTPStatus
from flask_cors import cross_origin
from flask import abort
import uuid


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):

        if 'Authorization' not in request.headers:
            abort(401)
            # It is important only abort the operation.
            # If there is a specific error message, the user will
            # know that the operation you are trying to access exists.

        auth_token = request.headers.get('Authorization')
        print(auth_token)

        if auth_token:
            try:
                # For this project we will ignore the correct implementation of security
                user_id = Account.decode_auth_token(auth_token.encode())
                # data = request.headers['Authorization'].encode('ascii', 'ignore')
                # token = str.replace(str(data), 'Bearer ', '')
                # token = Account.encode_auth_token(token)
            except:
                abort(401, {'status': 'fail', 'message': 'Something is wrong in the authentication'})
            return f(user_id, *args, **kws)
        else:
            abort(401)

    return decorated_function


# CONFIG
user_controller = Blueprint('user', __name__)


@user_controller.route('/user/login', methods=['POST'])
def login():
    """
        User Login Resource
    """
    code = HTTPStatus.OK
    msg = Message()

    print("O que vem como request: ", request.get_json())
    print(request.get_json()['user_id'])

    # Get parameters
    user_id = uuid.UUID(uuid.UUID(request.get_json()['user_id']).hex)
    password = request.get_json()['password']

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

            with_token = Active_Sessions.query.filter_by(user_id=user_id).first()
            if with_token is None:
                auth_token = Account.encode_auth_token(current_user.id)
                # mark the token into Active_Sessions
                active_session = Active_Sessions(token=auth_token, user_id=user_id)
                active_session.save_to_db()

                print("Devolvendo agora o token")
                if auth_token:
                    response = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
            else:
                auth_token = with_token.token
                print("Devolvendo agora o token0")
                #TODO: devolver um novo token e apagar o anterior
                if auth_token:
                    response = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.replace("b\'", "").replace("\'", "")
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


@user_controller.route('/user/logout', methods=['POST'])
@login_required
def logout(account_id):
    """
        Logout Resource
    """
    # get auth token
    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:
        if account.state:
            Active_Sessions.query.filter(Active_Sessions.user_id == account_id).delete()

            response = {
                'status': 'success',
                'message': 'Successfully logged out.'
            }
            return msg.message(code, response)
        else:
            code = HTTPStatus.UNAUTHORIZED
            response = {
                'status': 'fail',
                'message': ''
            }
            return msg.message(code, response)
    else:
        code = HTTPStatus.FORBIDDEN
        response = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return msg.message(code, response)


@user_controller.route('/user/check/<uuid:token>', methods=['POST'])
@login_required
def check_token(self, account_id, token):
    print("Quero saber o resultado disto: ", True if Active_Sessions.query.filter_by(token=token, user_id=account_id) else False)
    return True if Active_Sessions.query.filter_by(token=token, user_id=account_id) else False


@user_controller.route('/user/loginR', methods=['POST'])
def login_redirect():
    """
        User Login Resource
    """
    code = HTTPStatus.OK
    msg = Message()

    print("O que vem como request: ", request.get_json())
    print(request.get_json()['user_id'])

    # Get parameters
    user_id = uuid.UUID(uuid.UUID(request.get_json()['user_id']).hex)
    password = request.get_json()['password']

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

            with_token = Active_Sessions.query.filter_by(user_id=user_id).first()
            if with_token is None:
                auth_token = Account.encode_auth_token(current_user.id)
                # mark the token into Active_Sessions
                active_session = Active_Sessions(token=auth_token, user_id=user_id)
                active_session.save_to_db()

                print("Devolvendo agora o token")
                if auth_token:
                    response = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
            else:
                auth_token = with_token.token
                print("Devolvendo agora o token0")
                #TODO: devolver um novo token e apagar o anterior
                if auth_token:
                    response = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.replace("b\'", "").replace("\'", "")
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