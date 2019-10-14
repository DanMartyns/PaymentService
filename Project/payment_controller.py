from flask import Flask, jsonify, request, Blueprint
from auxiliar_functions import Auxiliar, Message
from models import db, Account, Payment, Transaction
from http import HTTPStatus
from iso4217 import Currency
import datetime
import uuid

# CONFIG
payment_controller = Blueprint('payment', __name__,)


@payment_controller.route('/account/<uuid:id>/payment', methods=['POST'])
def create_payment(id):
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
        seller_id = uuid.UUID(uuid.UUID(request.json.get('seller_id')).hex) 
        currency = request.json.get('currency').upper()
        reference = request.json.get('reference')

        # Check if there is some missing argument
        if not request_id or not seller_id or not currency or not reference:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Missing arguments")

        # Flag to check if account exists
        buyer = Account.query.get(id)
        receiver = Account.query.get(seller_id)        

        # Validate parameters
        if not aux.validate_uuid(id) or not aux.validate_uuid(seller_id) or not buyer or not receiver:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your number account or the number receiver account is wrong or they don't exist")

        account = Account.query.get(id)

        # Check if the currency is valid
        if not isinstance(Currency(currency), Currency):
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your currency is wrong. Uses the international standard that defines three-letter codes as currencies established by the International Organization. (ISO 4217)")

    except Exception as excep:
        return msg.message(code, str(excep))

    # Save the state of the payment
    # Everytime that we create a payment, his state is "pending"
    payment = Payment(request_id, id, seller_id, Currency(currency), reference)
    db.session.add(payment)
    db.session.commit()

    response = {
        'status': 'success',
        'id': payment.id
    }

    return msg.message(code, response)

# Get payment
@payment_controller.route('/account/<uuid:user_id>/payments', methods=['GET'])
def get_payments(user_id):
    """
        Get the payments from an User

        :param id: The id of the user to be fetched
        :type id: uuid

        :rtype: dict | bytes    
    """    

    code = HTTPStatus.OK
    msg = Message()
    aux = Auxiliar()

    try:
        account = Account.query.get(user_id)
        
        # Check if the id account is a uuid
        if not aux.validate_uuid(user_id):
            code = HTTPStatus.BAD_REQUEST
            raise Exception("The number account is not a universally unique identifier")

        # Check if the account exists
        if not account:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Account not found")

    except Exception as excep:
        return msg.message(code, str(excep))

    payments = Payment.query.filter_by(account_id=user_id)

    data = []
    for payment in payments :
        payment_data = {
            'id': payment.id,
            'request' : payment.request_id,
            'seller' : payment.receiver_id,
            'created_at' : payment.created_at,
            'state': payment.state.name,            
            'amount': payment.amount,
            'currency': payment.currency.name,
            'reference': payment.reference
        }
        data.append(payment_data)

    response = {
        'status': 'success',
        'payments': data
    }

    return msg.message(code, response)

# Create and request transaction
@payment_controller.route('/payment/<uuid:payment_id>/transactions', methods=['POST'])
def create_transaction(payment_id):
    """
        Add transaction to payment by ID

        :param payment_id: Id of the payment to be associated
        :type payment_id: int
        :param body: Transaction details
        :type body: dict | bytes

        :rtype: None
    """

    code = HTTPStatus.CREATED
    msg = Message()

    try:
        amount = request.json.get('amount')
        reference = request.json.get('reference')

        # Check if missing arguments
        if not amount or not reference:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("The amount or reference values is missing")

        payment = Payment.query.get(payment_id)

        # Check if payments exists
        if not payment:
            code = HTTPStatus.NOT_FOUND
            raise Exception("Payment not found")

        account = Account.query.get(payment.account_id)

        # Check if he is enough money to pay
        if amount > account.balance:
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your Account does not have enough available amount")

    except Exception as excep:
        return msg.message(code, str(excep))

    # Create a transaction
    transaction = Transaction(amount, payment_id, reference )
    db.session.add(transaction)

    payment.amount += amount

    db.session.commit()

    response = {
        'status': 'success',
        'id': transaction.id
    }

    return msg.message(code, response)

# Cancel a transaction
@payment_controller.route('/payment/<uuid:payment_id>/transactions/<uuid:transaction>/cancel', methods=['POST'])
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
            raise Exception("The transaction is already completed, you cannot cancel")

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
@payment_controller.route('/payment/<uuid:id>/execute', methods=['POST'])
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
    print(transactions)

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
            raise Exception("The account does not have enough available amount")

        # Check if the total of the transactions pays the amount of the payment
        print(total)
        print(payment.amount)
        if total != payment.amount :
            code = HTTPStatus.NOT_ACCEPTABLE
            raise Exception("The total of the transactions needs to be equals to the payment amount")

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
@payment_controller.route('/payment/<uuid:id>/authorize', methods=['POST'])
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
@payment_controller.route('/payment/<uuid:id>/transactions', methods=['GET'])
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
@payment_controller.route('/payment/<uuid:id>/transactions/<uuid:transaction>', methods=['GET'])
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

    transaction = Transaction.query.get(transaction)

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
