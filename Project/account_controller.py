from flask import Flask, jsonify, request, Blueprint
from auxiliar_functions import Auxiliar, Message
from models import db, Account, Payment
from http import HTTPStatus
from iso4217 import Currency
import datetime
import uuid

# CONFIG
account_controller = Blueprint('account', __name__,)


@account_controller.route('/account', methods=['POST'])
def create_account():
    """
        Add an account with a user id

        :rtype: dict | bytes
    """

    code = HTTPStatus.CREATED
    aux = Auxiliar()
    msg = Message()

    try:
        # Get parameters
        user_id = uuid.UUID(uuid.UUID(request.json.get('user_id')).hex) 
        currency = request.json.get('currency')
        
        # Validate the parameters
        if not aux.validate_uuid(user_id):
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your user_id is wrong. The user_id is not a universally unique identifier")
        elif isinstance(currency, Currency):
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your currency is wrong. Uses the international standard that defines three-letter codes as currencies established by the International Organization. (ISO 4217)")

    except Exception as excep:
        return msg.message(code, str(excep))

    # Save the account with the user id
    ac = Account(user_id=user_id, currency=Currency(currency))
    db.session.add(ac)
    db.session.commit()

    account = Account.query.get(ac.id)

    response = {
        'status': 'success',
        'account':
        {
            'id' : account.id,
            'user': account.user_id,
            'currency': account.currency.name,            
            'balance': account.balance,
            'state': 'active' if account.state else 'desactive',
            'created_at': account.created_at,
            'updated_at': account.updated_at
        }
    }

    # Return the information    
    return msg.message(code, response)    



@account_controller.route('/account/<uuid:id>/amount', methods=['POST'])
def add_amount(id):
    """
        Add an amount to an account

        :param id: The id of the account to be fetched
            :type id: int

            :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    aux = Auxiliar()
    msg = Message()

    try:
        # Get parameters
        amount = request.json.get('amount')

        # Flag to check if account exists
        account = Account.query.get(id)

        # Flag to check if the account is activated
        activated = db.Query(Account).filter_by(state = True)

        # Validate the parameters
        if not aux.validate_uuid(id) or not account:
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "Your number account is wrong. The number account is not a universally unique identifier or doesn't exist")
        elif not activated:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            raise Exception("Your number account is desactivated.")
        elif not isinstance(float(amount), float):
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your amount is wrong. The amount is not valid")
        elif float(amount) < 0.0:
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "Your amount is wrong. The amount needs to be more than 0.0")

    except Exception as excep:
        return msg.message(code, str(excep))

    # Update the total amount in his account
    account.balance += amount
    db.session.commit()

    response = {
        'status': 'success',
    }

    return msg.message(code, response)


@account_controller.route('/account/<uuid:id>/activate', methods=['POST'])
def activate_account(id):
    """
        Activate the user account

        :param id: The id of the user to be fetched
            :type id: int

            :rtype: dict | bytes    
    """

    code = HTTPStatus.OK
    aux = Auxiliar()
    msg = Message()

    try:
        # Flag to check if account exists
        account = Account.query.get(id)

        # Validate the parameters
        if not aux.validate_uuid(id) or not account:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your number account is wrong. The number account is not a universally unique identifier or doesn't exist")
        elif account.state:
            code = HTTPStatus.NOT_MODIFIED
            raise Exception("The account is already activated")
    except Exception as excep:
        return msg.message(code, str(excep))

    # Update the state of the account
    account.state = True
    db.session.commit()

    response = {
        'status': 'success',      
    }

    return msg.message(code, response)


@account_controller.route('/account/<uuid:id>/desactivate', methods=['POST'])
def desativate_account(id):
    """
        Desactivate the user account

        :param id: The id of the user to be fetched
            :type id: int

            :rtype: dict | bytes    
    """
    code = HTTPStatus.OK
    aux = Auxiliar()
    msg = Message()

    try:
        # Flag to check if account exists
        account = Account.query.get(id)

        # Validate the parameters
        if not aux.validate_uuid(id) or not account:
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "Your number account is wrong. The number account is not a universally unique identifier or doesn't exist")
        elif not account.state:
            code = HTTPStatus.NOT_MODIFIED
            raise Exception("The account is already desactivated")
    except Exception as excep:
        return msg.message(code, str(excep))

    # Update the total amount in his account
    account.state = False
    db.session.commit()

    response = {
        'status': 'success',
    }

    return msg.message(code, response)

# Get acount information
@account_controller.route('/account/<uuid:id>', methods=['GET'])
def account_info(id):
    """
        Get the account information

        :param id: Id of the account
        :type id: int

        :rtype: dict | bytes (with the Transaction)
    """

    code = HTTPStatus.OK
    msg = Message()
    aux = Auxiliar()

    try:
        account = Account.query.get(id)
        # Check if the id account is a uuid
        if not aux.validate_uuid(id):
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "The number account is not a universally unique identifier")

        # Check if the account exists
        if not account:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Account not found")

    except Exception as excep:
        return msg.message(code, str(excep))

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

    return msg.message(code, response)
