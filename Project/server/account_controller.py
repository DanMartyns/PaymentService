from flask import request, Blueprint
from server import db
from server.auxiliar_functions import Auxiliar, Message
from server.user_controller import login_required
from server.models import Account
from http import HTTPStatus
from iso4217 import Currency
import uuid

# CONFIG
account_controller = Blueprint('account', __name__)


@account_controller.route('/account', methods=['POST'])
def create_account():
    """
        Add an account with a user id

        :rtype: dict | bytes
    """
    code = HTTPStatus.CREATED
    aux = Auxiliar()
    msg = Message()

    user = Account.query.filter_by(user_id=uuid.UUID(uuid.UUID(request.json.get('user_id')).hex)).first()
    if not user:
        try:
            # Get parameters
            user_id = uuid.UUID(uuid.UUID(request.json.get('user_id')).hex)
            password = request.json.get('password')
            currency = request.json.get('currency').upper()

            # Validate the parameters
            if not aux.validate_uuid(user_id):
                code = HTTPStatus.BAD_REQUEST
                raise Exception("Your user_id is wrong. The user_id is not a universally unique identifier")
            elif not isinstance(Currency(currency), Currency):
                code = HTTPStatus.BAD_REQUEST
                raise Exception("Currency's wrong. Use the international standard that defines three-letter codes as "
                                "currencies established by the International Organization. (ISO 4217)")

            # Save the account
            ac = Account(user_id=user_id, password=password, currency=Currency(currency))
            db.session.add(ac)
            db.session.commit()

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
def add_amount(account):
    """
        Add an amount to an account

        :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    msg = Message()

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
        return msg.message(code,response)
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)


@account_controller.route('/account/activate', methods=['POST'])
@login_required
def activate_account(account):
    """
        Activate the user account

        :rtype: dict | bytes    
    """

    code = HTTPStatus.OK
    msg = Message()

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
            raise Exception("The account is already activated")
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)


@account_controller.route('/account/desactivate', methods=['POST'])
@login_required
def desativate_account(account):
    """
        Desactivate the user account

        :rtype: dict | bytes    
    """

    code = HTTPStatus.OK
    msg = Message()

    if account:
        if not account.state:
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
@account_controller.route('/account', methods=['GET'])
@login_required
def account_info(account):
    """
        Get the account information

        :rtype: dict | bytes (with the Transaction)
    """

    code = HTTPStatus.OK
    msg = Message()

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

