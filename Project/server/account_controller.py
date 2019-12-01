from flask import request, Blueprint, render_template
from server import db
from server.auxiliar_functions import Auxiliar, Message
from server.user_controller import login_required
from server.models import Account
from http import HTTPStatus
from iso4217 import Currency
from flask_cors import cross_origin
import uuid

# CONFIG
account_controller = Blueprint('account', __name__, template_folder='templates', static_folder='static/static')


@account_controller.route('/account/connection', methods=['GET'])
@cross_origin(supports_credentials=True)
def test_connection():
    msg = Message()
    response = {
        'status': 'success'
    }
    return msg.message(HTTPStatus.OK, response)


@account_controller.route('/account/trans', methods=['GET'])
def get_trans():
    msg = Message()
    transdev_account = Account.find_by_id("transdev")
    cp_account = Account.find_by_id("cp")
    metro_account = Account.find_by_id("metro")

    response = {
        'status': 'success',
        'carriers':
        {
            'Transdev': transdev_account.id,
            'CP': cp_account.id,
            'metro': metro_account.id
        }
    }
    return msg.message(HTTPStatus.OK, response)


@account_controller.route('/account/', methods=['POST'])
def create_account():
    """
        Add an account with a user id

        :rtype: dict | bytes
    """
    code = HTTPStatus.CREATED
    aux = Auxiliar()
    msg = Message()

    user = Account.query.filter_by(user_id=request.json.get('user_id')).first()
    if not user:
        try:
            # Get parameters
            user_id = request.json.get('user_id')
            password = request.json.get('password')
            currency = request.json.get('currency').upper()

            # Validate the parameters
            if not isinstance(Currency(currency), Currency):
                code = HTTPStatus.BAD_REQUEST
                response = {
                    'status': 'fail',
                    'message': "Currency's wrong. Use the international standard that defines three-letter codes as "
                                "currencies established by the International Organization. (ISO 4217)"
                }
            else:
                # Save the account
                ac = Account(user_id=user_id, password=password, currency=Currency(currency))
                ac.save_to_db()

                response = {
                    'status': 'success',
                    'account':
                    {
                        'id': ac.id,
                        'user': ac.user_id,
                        'password': ac.password,
                        'currency': ac.currency.name,
                        'balance': ac.balance,
                        'state': 'active' if ac.state else 'desactive',
                        'created_at': ac.created_at,
                        'updated_at': ac.updated_at
                    }
                }
        except Exception as exc:
            code = HTTPStatus.INTERNAL_SERVER_ERROR
            response = {
                'status': 'fail',
                'message': str(exc)
            }
    else:
        code = HTTPStatus.ACCEPTED
        response = {
            'status': 'fail',
            'message': 'User already exists. Please Log in'
        }

    # Return the information
    return msg.message(code, response)


@account_controller.route('/account/amount', methods=['POST'])
@login_required
def add_amount(account_id):
    """
        Add an amount to an account

        :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:

        if account.state:
            try:
                # Get parameters
                amount = request.json.get('amount')

                # Validate the parameters
                if not isinstance(float(amount), float):
                    code = HTTPStatus.BAD_REQUEST
                    raise Exception("Your amount is wrong. The amount is not valid")

                elif float(amount) < 0.0:
                    code = HTTPStatus.BAD_REQUEST
                    raise Exception("Your amount is wrong. The amount needs to be more than 0.0")
            except Exception as excep:
                response = {
                    'status': 'fail',
                    'message': str(excep)
                }

            # Update the total amount in his account
            account.balance += amount
            db.session.commit()

            response = {
                'status': 'success',
                'message': 'The amount was added.'
            }

        else:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response = {
                'status': 'fail',
                'message': 'Your number account is desactivated.'
            }
        return msg.message(code, response)
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)


@account_controller.route('/account/activate', methods=['POST'])
@login_required
def activate_account(account_id):
    """
        Activate the user account

        :rtype: dict | bytes    
    """

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:

        if not account.state:
            # Update the state of the account
            account.state = True
            db.session.commit()

            response = {
                'status': 'success',
                'message': 'Successfully activated.',
            }
        else:
            code = HTTPStatus.NOT_MODIFIED
            response = "The account is already activated"
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)


@account_controller.route('/account/desactivate', methods=['POST'])
@login_required
def desativate_account(account_id):
    """
        Desactivate the user account

        :rtype: dict | bytes    
    """

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:
        if account.state:
            account.state = False
            db.session.commit()

            response = {
                'status': 'success',
                'message': 'Successfully desactivated.',
            }
        else:
            code = HTTPStatus.NOT_MODIFIED
            response = {
                'status': 'fail',
                'message': 'The account is already desactivated'
            }
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)

# Get account information
@account_controller.route('/account/', methods=['GET'])
@login_required
def account_info(account_id):
    """
        Get the account information

        :rtype: dict | bytes (with the Transaction)
    """

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:
        response = {
            'status': 'success',
            'account':
            {
                'id': account.id,
                'user': account.user_id,
                'balance': account.balance,
                'currency': account.currency.name,
                'state': 'active' if account.state else 'desactive',
                'created_at': account.created_at,
                'updated_at': account.updated_at
            }
        }
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        } 

    return msg.message(code, response)


@account_controller.route('/account/login', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def login():
    return render_template('login.html')
