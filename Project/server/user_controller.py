from flask import request, Blueprint, session
from server import db
from server.models import Account, Active_Sessions
from server.auxiliar_functions import Message
from functools import wraps
from http import HTTPStatus
from flask import abort
import uuid


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        msg = Message()
        auth_header = request.headers.get('Authorization')
        if 'logged_in' in session:
            if auth_header:
                try:
                    auth_token = auth_header.split(" ")[1]
                    print(auth_token)
                except IndexError:
                    abort(400, {'status': 'fail', 'message': 'Bad format message'})
            else:
                auth_token = ''

            if auth_token:
                try:
                    resp = Account.decode_auth_token(auth_token)
                    data = request.headers['Authorization'].encode('ascii', 'ignore')
                    token = str.replace(str(data), 'Bearer ', '')
                    token = Account.encode_auth_token(token)
                except:
                    abort(401)
                return f(token, *args, **kws)
            else:
                abort(401)
        else:
            abort(401, {'status': 'fail', 'message': 'Login first'})

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
    print(password)
    try:
        # fetch the user data
        user = Account.query.filter_by(user_id=user_id).first()
        print(user.__dict__)

        if user and Account.check_password_hash(user.password, password):
            auth_token = Account.encode_auth_token(user.id)

            # mark the token into Active_Sessions
            active_session = Active_Sessions(token=auth_token)
            db.session.add(active_session)
            db.session.commit()

            if auth_token:
                session['logged_in'] = True
                response = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token.decode()
                }
                return msg.message(code, response)
        else:
            code = HTTPStatus.NOT_FOUND
            response = {
                'status': 'fail',
                'message': 'User does not exist.'
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
            session.pop('logged_in', None)
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
