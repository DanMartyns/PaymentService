from flask import request, Blueprint, render_template
from server.auxiliar_functions import Auxiliar, Message
from server.models import Account, Payment, Transaction, PaymentState, TransactionState
from server.user_controller import login_required
from flask_cors import cross_origin
from http import HTTPStatus
from iso4217 import Currency
import datetime
import uuid


# CONFIG
payment_controller = Blueprint('payment', __name__, template_folder='templates', static_folder='static/static')


@payment_controller.route('/payments/connection', methods=['GET'])
@cross_origin(supports_credentials=True)
def test_connection():
    msg = Message()
    response = {
        'status': 'success'
    }
    return msg.message(HTTPStatus.OK, response)


@payment_controller.route('/payments/', methods=['POST'])
@login_required
def create_payment(account_id):
    """
        Make a payment

        :rtype: dict | bytes
    """

    code = HTTPStatus.CREATED
    aux = Auxiliar()
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:
        try:
            # Get parameters
            request_id = request.json.get('request_id')
            seller_id = uuid.UUID(uuid.UUID(request.json.get('seller_id')).hex) 
            currency = request.json.get('currency').upper()
            reference = request.json.get('reference')

            # Check if there is some missing argument
            if not request_id or not seller_id or not currency or not reference:
                code = HTTPStatus.BAD_REQUEST
                response = {
                    'status': 'fail',
                    'message': 'Missing arguments.'
                }
                return msg.message(code, response)

            # Flag to check if account exists
            receiver = Account.query.get(seller_id)

            # Validate parameters
            if not aux.validate_uuid(seller_id) or not receiver:
                code = HTTPStatus.BAD_REQUEST
                response = {
                    'status': 'fail',
                    'message': 'The number receiver account is wrong or they dont exist.'
                }
                return msg.message(code, response)

            # Check if the currency is valid
            if not isinstance(Currency(currency), Currency):
                code = HTTPStatus.BAD_REQUEST
                response = {
                    'status': 'fail',
                    'message': 'Your currency is wrong. Uses the international standard that defines three-letter "\
                                "codes as currencies established by the International Organization. (ISO 4217).'
                }
                return msg.message(code, response)

        except Exception as exc:
            code = HTTPStatus.INTERNAL_SERVER_ERROR
            response = {
                'status': 'fail',
                'message': str(exc)
            }

        # Save the new payment
        # Everytime that we create a payment, his state is "pending"
        payment = Payment(request_id, account.id, seller_id, Currency(currency), reference)
        payment.save_to_db()

        response = {
            'status': 'success',
            'id': payment.id
        }
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }        

    return msg.message(code, response)

# Get payment
@payment_controller.route('/payments/', methods=['GET'])
@login_required
def get_payments(account_id):
    """
        Get the payments from an User

        :rtype: dict | bytes    
    """    

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:
        try:
            payments = Payment.query.filter_by(account_id=account.id)

            data = []
            for payment in payments:
                payment_data = {
                    'id': payment.id,
                    'request': payment.request_id,
                    'seller': payment.receiver_id,
                    'created_at': payment.created_at,
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
        except Exception as err:
            code = HTTPStatus.INTERNAL_SERVER_ERROR
            response = {
                'status': 'fail',
                'message': str(err)
            }

    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }   

    return msg.message(code, response)

# Create and request transaction
@payment_controller.route('/payments/<uuid:payment_id>/transactions', methods=['POST'])
@login_required 
def create_transaction(account_id, payment_id):
    """
        Add transaction to payment by ID

        :param account_id: Account id
        :type account_id: uuid
        :param payment_id: Id of the payment to be associated
        :type payment_id: uuid

        :rtype: dict | bytes (Transaction details)
    """

    code = HTTPStatus.CREATED
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:
        
        if account.state:
            try:
                amount = request.json.get('amount')
                reference = request.json.get('reference')

                # Check if missing arguments
                if not amount or not reference:
                    code = HTTPStatus.BAD_REQUEST
                    response = {
                        'status': 'fail',
                        'message': "The amount or reference values is missing"
                    }
                    return msg.message(code, response)

                payment = Payment.query.get(payment_id)

                # Check if payments exists
                if not payment:
                    code = HTTPStatus.NOT_FOUND
                    response = {
                        'status': 'fail',
                        'message': "Payment not found"
                    }
                    return msg.message(code, response)

            except Exception as excep:
                return msg.message(code, str(excep))

            # Create a transaction
            transaction = Transaction(amount, payment_id, reference)
            transaction.save_to_db()

            payment.amount += amount

            response = {
                'status': 'success',
                'id': transaction.id
            }                
        else:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response = {
                'status': 'fail',
                'message': 'Your number account is desactivated.'
            }  
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)

# Cancel a transaction
@payment_controller.route('/payments/<uuid:payment_id>/transactions/<uuid:transaction>/cancel', methods=['POST'])
@login_required
def cancel_transaction(account_id, payment_id, transaction):
    """
        Cancel transaction from payment by the ID of the transaction

        :param account_id: Account id
        :type account_id: uuid
        :param payment_id: Id of the payment
        :type payment_id: uuid
        :param transaction: Id of the transaction
        :type transaction: uuid

        :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    msg = Message()

    try:
        account = Account.query.filter_by(id=account_id).first()

        if account:
            if account.state:
                try:

                    payment = Payment.query.get(payment_id)

                    # Check if payments exists
                    if not payment:
                        code = HTTPStatus.NOT_FOUND
                        response = {
                            'status': 'fail',
                            'message': "Payment not found"
                        }
                        return msg.message(code, response)

                    transaction = Transaction.query.get(transaction)

                    # Check if transaction exists
                    if not transaction:
                        code = HTTPStatus.NOT_FOUND
                        response = {
                            'status': 'fail',
                            'message': "Transaction not found"
                        }
                        return msg.message(code, response)

                    if transaction.state == PaymentState("completed"):
                        code = HTTPStatus.CONFLICT
                        response = {
                            'status': 'fail',
                            'message': "The transaction is already completed, you cannot cancel"
                        }
                        return msg.message(code, response)

                    # Calculate the amount that will no longer be included in the final payment
                    diff = payment.amount - transaction.amount

                    payment.amount -= diff

                    # The transaction was cancelled
                    transaction.state = PaymentState("cancelled")

                    response = {
                        'status': 'success',
                        'message': 'The transaction '+str(transaction.id)+' was cancelled'
                    }

                except Exception as exc:
                    response = {
                        'status': 'fail',
                        'message': str(exc)
                    }
            else:
                code = HTTPStatus.METHOD_NOT_ALLOWED
                response = {
                    'status': 'fail',
                    'message': 'Your number account is desactivated.'
                }
        else:
            code = HTTPStatus.INTERNAL_SERVER_ERROR
            response = {
                'status': 'fail',
                'message': 'Try Again.'
            }
    except Exception as err:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': str(err)
        }
    return msg.message(code, response)

# Execute the payment
@payment_controller.route('/payments/<uuid:payment_id>/execute', methods=['GET', 'POST'])
@login_required
def execute(account_id, payment_id):
    """
        Execute payment by ID

        :param account_id: Account id
        :type account_id: uuid
        :param payment_id: Id of the payment to be executed
        :type payment_id: uuid

        :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:

        if account.state:
            try:

                payment = Payment.query.get(payment_id)

                # Check if payments exists
                if not payment:
                    code = HTTPStatus.NOT_FOUND
                    response = {
                        'status': 'fail',
                        'message': "Payment not found"
                    }
                    return msg.message(code, response)

                if payment.state == PaymentState("completed"):
                    code = HTTPStatus.CONFLICT
                    response = {
                        'status': 'fail',
                        'message': "The payment is already completed"
                    }
                    return msg.message(code, response)

                if payment.state == PaymentState("authorized"):

                    transactions = Transaction.query.filter_by(id_payment=payment_id, state="created")

                    total = 0.0

                    for t in transactions:
                        t.state = "completed"
                        total += t.amount

                    try:

                        # Check if he is enough money to pay
                        if total > account.balance:
                            code = HTTPStatus.NOT_ACCEPTABLE
                            response = {
                                'status': 'fail',
                                'message': "The account does not have enough available amount"
                            }
                            return msg.message(code, response)

                        seller = Account.query.get(payment.receiver_id)
                        seller.balance += total

                        account.balance -= total
                        payment.state = PaymentState("completed")

                        response = {
                            'status': 'success',
                            'message': 'The payment was executed'
                        }
                    except Exception as exc:
                        code = HTTPStatus.INTERNAL_SERVER_ERROR
                        response = {
                            'status': 'fail',
                            'message': str(exc)
                        }
                else:
                    code = HTTPStatus.METHOD_NOT_ALLOWED
                    response = {
                        'status': 'fail',
                        'message': 'Payment not authorized.'
                    }
            except Exception as exc:
                code = HTTPStatus.INTERNAL_SERVER_ERROR
                response = {
                    'status': 'fail',
                    'message': str(exc)
                }
        else:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response = {
                'status': 'fail',
                'message': 'Your number account is desactivated.'
            }
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)


# Authorize the payment
@payment_controller.route('/payments/<uuid:payment_id>/authorize', methods=['POST'])
@login_required
def authorization_payment(account_id, payment_id):
    """
        Authorization the payment

        :param account_id: Account id
        :type : uuid
        :param payment_id: Id of the payment
        :type payment_id: int

        :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:

        if account.state:
            try:
                payment = Payment.query.get(payment_id)

                # Check if payments exists
                if not payment:
                    code = HTTPStatus.NOT_FOUND
                    response = {
                        'status': 'fail',
                        'message': "Payment not found"
                    }
                    return msg.message(code, response)

                if payment.state == PaymentState("completed"):
                    code = HTTPStatus.CONFLICT
                    response = {
                        'status': 'fail',
                        'message': "The payment is already completed"
                    }
                    return msg.message(code, response)

                if payment.state == PaymentState("pending"):
                    payment.update_state("requested")

                response = {
                    'status': 'success',
                    'payment': payment_id,
                    'message': 'http://192.168.85.208/payments/'+str(payment_id)+'/authorize/request'
                }

            except Exception as exc:
                code = HTTPStatus.INTERNAL_SERVER_ERROR
                response = {
                    'status': 'fail',
                    'message': str(exc)
                }

        else:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response = {
                'status': 'fail',
                'message': 'Your number account is desactivated.'
            }  
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)


@payment_controller.route('/payments/<uuid:payment_id>/authorize/request', methods=['GET', 'POST'])
def authorize(payment_id):
    code = HTTPStatus.OK
    msg = Message()

    try:

        payment = Payment.query.filter_by(id=payment_id).first()
        account_buyer = Account.query.filter_by(id=payment.account_id).first()
        account_seller = Account.query.filter_by(id=payment.receiver_id).first()

        payment_data = {
            'id': payment.id,
            'buyer_user_id': str(account_buyer.user_id),
            'buyer': str(account_buyer.id),
            'seller_user_id': str(account_seller.user_id),
            'seller': str(account_seller.id),
            'created_at': payment.created_at,
            'state': payment.state.name,
            'amount': payment.amount,
            'currency': payment.currency.name,
            'reference': payment.reference
        }

        transactions = Transaction.query.filter_by(id_payment=payment_id)

        data = []
        for transaction in transactions:
            transaction_data = {
                'amount': transaction.amount,
                'emission_date': transaction.emission_date.date(),
                'emission_time': transaction.emission_date.strftime("%H:%M:%S"),
                'state': transaction.state.name,
                'update_date': transaction.update_date,
                'reference': transaction.reference
            }
            data.append(transaction_data)

        if payment.state == PaymentState("requested"):
            return render_template('index.html', payment=payment_data, transactions=data)
        else:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response = {
                'status': 'fail',
                'message': 'You dont have any authorization request.'
            }

    except Exception as exc:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': str(exc)
        }

    return msg.message(code, response)


@payment_controller.route('/payments/<uuid:payment_id>/authorize/response', methods=['GET', 'POST'])
def authorize_response(payment_id):
    code = HTTPStatus.OK
    msg = Message()

    try:

        payment = Payment.query.get(payment_id)

        if payment.state != PaymentState("requested"):
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response = {
                'status': 'fail',
                'message': 'You dont have any authorization request.'
            }
            return msg.message(code, response)

        payment.update_state("authorized")

        transactions = Transaction.query.filter_by(id_payment=payment_id)

        for t in transactions:
            t.update_state("authorized")

        response = {
            'status': 'success',
            'message': 'Your payment was authorized.'
        }

    except Exception as exc:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': str(exc)
        }
    return msg.message(code, response)

# Get all the transactions
@payment_controller.route('/payments/<uuid:payment_id>/transactions', methods=['GET'])
@login_required
def get_transactions(account_id, payment_id):
    """
        Find transactions from payment by ID

        :param account_id: Account_id
        :type account_id: uuid
        :param payment_id: Id of the payment associated
        :type payment_id: uuid

        :rtype: dict | bytes (with Transactions)
    """

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:
        
        if account.state:
            try:
                payment = Payment.query.get(payment_id)

                # Check if payments exists
                if not payment:
                    code = HTTPStatus.NOT_FOUND
                    response = {
                        'status': 'fail',
                        'message': "Payment not found"
                    }

                transactions = Transaction.query.filter_by(id_payment=payment_id)

                data = []
                for transaction in transactions:
                    transaction_data = {
                        'id': transaction.id,
                        'amount': transaction.amount,
                        'emission_date': transaction.emission_date,
                        'state': transaction.state.name,
                        'update_date': transaction.update_date,
                        'id_payment': transaction.id_payment,
                        'reference': transaction.reference
                    }
                    data.append(transaction_data)

                response = {
                    'status': 'success',
                    'transactions': data
                }
            except Exception as excep:
                code = HTTPStatus.INTERNAL_SERVER_ERROR
                response = {
                    'status': 'fail',
                    'message': str(excep)
                }
        else:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response = {
                'status': 'fail',
                'message': 'Your number account is desactivated.'
            }
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }

    return msg.message(code, response)

# Get a specific transaction
@payment_controller.route('/payments/<uuid:payment_id>/transactions/<uuid:transaction>', methods=['GET'])
@login_required
def get_transaction(account_id, payment_id, transaction):
    """
        Find transactions from payment by ID

        :param account_id: Account id
        :type account_id: uuid
        :param payment_id: Id of the payment associated
        :type payment_id: uuid
        :param transaction: A specific transaction of a payment
        :type transaction: uuid

        :rtype: dict | bytes (with the Transaction)
    """

    code = HTTPStatus.OK
    msg = Message()

    account = Account.query.filter_by(id=account_id).first()

    if account:
        
        if account.state:
            try:
                payment = Payment.query.get(payment_id)

                # Check if payments exists
                if not payment:
                    code = HTTPStatus.NOT_FOUND
                    response = {
                        'status': 'fail',
                        'message': "Payment not found"
                    }
                    return msg.message(code, response)

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
            except Exception as excep:
                code = HTTPStatus.INTERNAL_SERVER_ERROR
                response = {
                    'status': 'fail',
                    'message': str(excep)
                }
        else:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response = {
                'status': 'fail',
                'message': 'Your number account is desactivated.'
            }  
    else:
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        response = {
            'status': 'fail',
            'message': 'Try Again.'
        }
    return msg.message(code, response)
