from flask import Flask, jsonify, request, Blueprint
from auxiliar_functions import Auxiliar, Message
from models import db, Account, Payment
from http import HTTPStatus
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
        user_id = request.json.get('user_id')
        currency = request.json.get('currency')

        # Validate the parameters
        if not aux.validate_uuid(user_id):
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "Your user_id is wrong. The user_id is not a universally unique identifier")
        elif currency not in aux.currency_codes():
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "Your currency is wrong. Uses the international standard that defines three-letter codes as currencies established by the International Organization. (ISO 4217)")

    except Exception as excep:
        return msg.message(code, str(excep))

    # Save the account with the user id
    account = Account(user_id=user_id, currency=currency)
    db.session.add(account)
    db.session.commit()

    # Return the information
    date = datetime.datetime.utcnow().isoformat()
    return msg.message(code, jsonify(id=uuid.uuid4(), user_id=user_id, balance=0, currency=currency, state="activate", created_at=date, updated_at=date))


@account_controller.route('/account/<int:id>/amount', methods=['POST'])
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
        exists = db.Query(Account).filter_by(Account.id.contains(id))
        print(exists)

        # Flag to check if the account is activated
        activated = db.Query(Account).filter_by(Account.state == True)

        # Validate the parameters
        if not aux.validate_uuid(id) or not exists:
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
    db.update(Account).values(balance=amount).where(id == id)
    db.commit()

    response = {
        'status': 'success',
    }

    return msg.message(code, response)


@account_controller.route('/account/<int:id>/activate', methods=['POST'])
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
        exists = db.Query(Account).filter_by(Account.id.contains(id))
        print(exists)

        # Flag to check if the account is activated
        activated = db.Query(Account).filter_by(Account.state == True)

        # Validate the parameters
        if not aux.validate_uuid(id) or not exists:
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "Your number account is wrong. The number account is not a universally unique identifier or doesn't exist")
        elif activated:
            code = HTTPStatus.NOT_MODIFIED
            raise Exception("The account is already activated")
    except Exception as excep:
        return msg.message(code, str(excep))

    # Update the state of the account
    db.update(Account).values(state=True).where(id == id)
    db.commit()

    response = {
        'status': 'success',
    }

    return msg.message(code, response)


@account_controller.route('/account/<int:id>/desactivate', methods=['POST'])
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
        exists = db.Query(Account).filter_by(Account.id.contains(id))
        print(exists)

        # Flag to check if the account is activated
        activated = db.Query(Account).filter_by(Account.state == True)

        # Validate the parameters
        if not aux.validate_uuid(id) or not exists:
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "Your number account is wrong. The number account is not a universally unique identifier or doesn't exist")
        elif not activated:
            code = HTTPStatus.NOT_MODIFIED
            raise Exception("The account is already desactivated")
    except Exception as excep:
        return msg.message(code, str(excep))

    # Update the total amount in his account
    db.update(Account).values(state=False).where(id == id)
    db.commit()

    response = {
        'status': 'success',
    }

    return msg.message(code, response)

# Get acount information
@account_controller.route('/account/<int:id>', methods=['GET'])
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
                'user_id': account.user_id,
                'balance': account.balance,
                'currency': account.currency,
                'state': account.state.name,
                'created_at': account.created_at,
                'updated_at': account.updated_at
            }
        }

    return msg.message(code, response)
