from flask import Flask, jsonify, request, Blueprint
from auxiliar_functions import Auxiliar, Message
from models import db, Account, Payment, Transaction
from http import HTTPStatus
import datetime
import uuid

# CONFIG
payment_controller = Blueprint('payment', __name__,)


@payment_controller.route('/payment', methods=['POST'])
def create_payment():
    """
        Make a payment

        :rtype: dict | bytes
    """

    code = HTTPStatus.CREATED
    aux = Auxiliar()
    msg = Message()

    try:
        # Get parameters
        request_id = request.json.get('request_id')
        account_id = request.json.get('account_id')
        receiving_id = request.json.get('receiving_id')
        amount = request.json.get('amount')
        currency = request.json.get('currency')
        reference = request.json.get('reference')

        # Check if there is some missing argument
        if not request_id or not account_id or not receiving_id or not amount or not currency or not reference:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Missing arguments")

        # Flag to check if account exists
        exists = db.Query(Account).filter_by(Account.id.contains(account_id)) and db.Query(Account).filter_by(Account.id.contains(receiving_id))
        print(exists)

        # Validate parameters
        if aux.validate_uuid(account_id) and aux.validate_uuid(receiving_id) and exists:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your number account or the number receiver account is wrong or they don't exist")

        account = Account.query.get(account_id)

        # Check if the amount is a float and positive value
        if not isinstance(float(amount), float) and float(amount) < 0.0:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("The amount needs to be a float and positive value")

        # Check if buyer has minimum amount available
        if account.balance < amount:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your account doesn't have minimum amount available")
        # Check if the currency is valid
        elif currency not in aux.currency_codes():
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your currency is wrong. Uses the international standard that defines three-letter codes as currencies established by the International Organization. (ISO 4217)")

    except Exception as excep:
        return msg.message(code, str(excep))

    # Save the state of the payment
    # Everytime that we create a payment, his state is "pending"
    payment = Payment(request_id, account_id, receiving_id, amount, currency, reference)
    db.session.add(payment)
    db.session.commit()

    response = {
        'status': 'success',
        'id': payment.id
    }

    return msg.message(code, response)

# Create and request transaction
@payment_controller.route('/payment/<int:payment_id>/transactions', methods=['POST'])
def create_transaction(id):
    """
        Add transaction to payment by ID

        :param id: Id of the payment to be associated
        :type id: int
        :param body: Transaction details
        :type body: dict | bytes

        :rtype: None
    """

    code = HTTPStatus.CREATED
    msg = Message()

    try:
        amount = request.json.get('amount')

        # Check if missing arguments
        if not amount:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("The amount value is missing")

        payment = Payment.query.get(id)

        # Check if payments exists
        if not payment:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Payment not found")

        account = Account.query.get(payment.account_id)

        # Check if he is enough money to pay
        if amount > account.balance:
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "Your Account does not have enough available amount")

    except Exception as excep:
        return msg.message(code, str(excep))

    # Create a transaction
    transaction = Transaction(amount, id)
    db.session.add(transaction)

    payment.amount += amount

    db.session.commit()

    response = {
        'status': 'success',
        'id': transaction.id
    }

    return msg.message(code, response)

# Cancel a transaction
@payment_controller.route('/payment/<int:payment_id>/transactions/<int:transaction>/cancel', methods=['POST'])
def cancel_transaction(payment_id, transaction):
    """
        Cancel transaction from payment by the ID of the transaction

        :param payment_id: Id of the payment
        :type payment_id: int
        :param transaction: Id of the transaction
        :type transaction: int

        :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    msg = Message()

    try:

        payment = Payment.query.get(payment_id)

        # Check if payments exists
        if not payment:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Payment not found")

        transaction = Transaction.query.get(transaction)

        # Check if transaction exists
        if not transaction:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Transaction not found")

        if transaction.state == "completed":
            code = HTTPStatus.CONFLICT
            raise Exception(
                "The transaction is already completed, you cannot cancel")

    except Exception as excep:
        return msg.message(code, str(excep))

    # Calculate the amount that will no longer be included in the final payment
    diff = payment.amount - transaction.amount

    payment.amount -= diff

    # The transaction was cancelled
    transaction.state = "cancelled"

    db.session.commit()

    response = {
        'status': 'sucess'
    }

    return msg.message(code, response)

# Execute the payment
@payment_controller.route('/payment/<int:id>/execute', methods=['POST'])
def execute(id):
    """
        Execute payment by ID

        :param id: Id of the payment to be executed
        :type id: int

        :rtype: dict | bytes
    """

    code = HTTPStatus.CREATED
    msg = Message()

    try:

        payment = Payment.query.get(id)

        # Check if payments exists
        if not payment:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Payment not found")

        if payment.state == "completed":
            code = HTTPStatus.CONFLICT
            raise Exception("The payment is already completed")

    except Exception as excep:
        return msg.message(code, str(excep))

    transactions = Transaction.query.filter_by(id_payment=id, state="created")

    total = 0.0
    for t in transactions:
        t.state = "completed"
        db.session.commit()
        total += t.amount

    try:
        buyer = Account.query.get(payment.account_id)

        # Check if he is enough money to pay
        if total > buyer.balance:
            code = HTTPStatus.BAD_REQUEST
            raise Exception(
                "The account does not have enough available amount")

    except Exception as excep:
        return msg.message(code, str(excep))

    seller = Account.query.get(payment.receiver_id)
    seller.balance += total

    buyer.balance -= total

    payment.state = "completed"

    db.session.commit()

    response = {
        'status': 'sucess'
    }

    return msg.message(code, response)


# Authorize the payment
@payment_controller.route('/payment/<int:id>/authorize', methods=['POST'])
def authorization_payment(id):
    """
        Authorization the payment

        :param payment_id: Id of the payment
        :type payment_id: int

        :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    msg = Message()

    try:
        payment = Payment.query.get(id)

        # Check if payments exists
        if not payment:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Payment not found")

        if payment.state == "completed":
            code = HTTPStatus.CONFLICT
            raise Exception('The payment is already completed')

    except Exception as excep:
        return msg.message(code, str(excep))

    # Let's pretend there is an authorization, and you need to call an "authorization" function, but nothing happens internally.

    response = {
        'status': 'sucess'
    }

    return msg.message(code, response)

# Get all the transactions
@payment_controller.route('/payment/<int:id>/transactions', methods=['GET'])
def get_transactions(id):
    """
        Find transactions from payment by ID

        :param id: Id of the payment associated
        :type id: int

        :rtype: dict | bytes (with Transactions)
    """

    code = HTTPStatus.OK
    msg = Message()

    try:
        payment = Payment.query.get(id)

        # Check if payments exists
        if not payment:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Payment not found")

    except Exception as excep:
        return msg.message(code, str(excep))

        transactions = Transaction.query.filter_by(id_payment=id)

    data = []
    for transaction in transactions:
        transaction_data = {
            'id': transaction.id,
            'amount': transaction.amount,
            'emission_date': transaction.emission_date,
            'state': transaction.state.name,
            'update_date': transaction.update_date,
            'id_payment': transaction.id_payment
        }
        data.append(transaction_data)

        response = {
            'status': 'success',
            'transactions': data
        }

    return msg.message(code, response)

# Get a specific transaction
@payment_controller.route('/payment/<int:id>/transactions/<int:transaction>', methods=['GET'])
def get_transaction(id, transaction):
    """
        Find transactions from payment by ID

        :param id: Id of the payment associated
        :type id: int
        :param transaction: A specific transaction of a payment
        :type transaction: int

        :rtype: dict | bytes (with the Transaction)
    """

    code = HTTPStatus.OK
    msg = Message()

    try:
        payment = Payment.query.get(id)

        # Check if payments exists
        if not payment:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Payment not found")

    except Exception as excep:
        return msg.message(code, str(excep))

    transaction = Transaction.query.filter_by(id_payment=id, id=transaction)

    response = {
        'status': 'success',
        'transaction':
        {
            'id': transaction.id,
            'amount': transaction.amount,
            'emission_date': transaction.emission_date,
            'state': transaction.state.name,
            'update_date': transaction.update_date,
            'id_payment': transaction.id_payment
        }
    }

    return msg.message(code, response)
