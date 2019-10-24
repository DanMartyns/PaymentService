from flask import request, Blueprint
from server import db
from server.auxiliar_functions import Auxiliar, Message
from server.models import Account, Payment, Transaction
from server.user_controller import login_required
from http import HTTPStatus
from iso4217 import Currency
import uuid

# CONFIG
payment_controller = Blueprint('payment', __name__)


@payment_controller.route('/payments', methods=['POST'])
@login_required
def create_payment(account):
    """
        Make a payment

        :rtype: dict | bytes
    """

    code = HTTPStatus.CREATED
    aux = Auxiliar()
    msg = Message()

    if account :
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
            receiver = Account.query.get(seller_id)        

            # Validate parameters
            if not aux.validate_uuid(seller_id) or not receiver:
                code = HTTPStatus.BAD_REQUEST
                raise Exception("The number receiver account is wrong or they don't exist")

            # Check if the currency is valid
            if not isinstance(Currency(currency), Currency):
                code = HTTPStatus.BAD_REQUEST
                raise Exception("Your currency is wrong. Uses the international standard that defines three-letter codes as currencies established by the International Organization. (ISO 4217)")

        except Exception as exc:
            response = {
                'status': 'fail',
                'message': str(exc)
            }                    
        # Save the state of the payment
        # Everytime that we create a payment, his state is "pending"
        payment = Payment(request_id, id, seller_id, Currency(currency), reference)
        db.session.add(payment)
        db.session.commit()

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
@payment_controller.route('/payments', methods=['GET'])
@login_required
def get_payments(account):
    """
        Get the payments from an User

        :rtype: dict | bytes    
    """    

    code = HTTPStatus.OK
    msg = Message()

    if account : 
        payments = Payment.query.filter_by(account_id=account.id)

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
def create_transaction(account, payment_id):
    """
        Add transaction to payment by ID

        :param account:
        :param payment_id: Id of the payment to be associated
        :type payment_id: int

        :rtype: dict | bytes (Transaction details)
    """

    code = HTTPStatus.CREATED
    msg = Message()

    if account:
        
        if account.state:
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

                # Check if he is enough money to pay
                if amount > account.balance:
                    code = HTTPStatus.BAD_REQUEST
                    raise Exception("Your Account does not have enough available amount")

            except Exception as excep:
                return msg.message(code, str(excep))

            # Create a transaction
            transaction = Transaction(amount, payment_id, reference)
            payment.amount += amount

            response = {
                'status': 'success',
                'id': transaction.id
            }                
        else :
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
def cancel_transaction(account,payment_id, transaction):
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
    
    if account:
        if account.state:
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

            except Exception as exc:
                response = {
                    'status': 'fail',
                    'message': str(exc)
                }

            # Calculate the amount that will no longer be included in the final payment
            diff = payment.amount - transaction.amount

            payment.amount -= diff

            # The transaction was cancelled
            transaction.state = "cancelled"

            response = {
                'status': 'success',
                'message' : 'The transaction '+transaction.id+' was cancelled'
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

# Execute the payment
@payment_controller.route('/payments/<uuid:id>/execute', methods=['POST'])
@login_required
def execute(account,id):
    """
        Execute payment by ID

        :param id: Id of the payment to be executed
        :type id: int

        :rtype: dict | bytes
    """

    code = HTTPStatus.CREATED
    msg = Message()
    if account :
        
        if account.state:
            try:

                payment = Payment.query.get(id)

                # Check if payments exists
                if not payment:
                    code = HTTPStatus.NOT_FOUND
                    raise Exception("Payment not found")

                if payment.state == "completed":
                    code = HTTPStatus.CONFLICT
                    raise Exception("The payment is already completed")

            except Exception as exc:
                response = {
                    'status': 'fail',
                    'message': str(exc)
                }

            transactions = Transaction.query.filter_by(id_payment=id, state="created")

            total = 0.0
            for t in transactions:
                t.state = "completed"
                total += t.amount

            try:

                # Check if he is enough money to pay
                if total > account.balance:
                    code = HTTPStatus.BAD_REQUEST
                    raise Exception("The account does not have enough available amount")

                # Check if the total of the transactions pays the amount of the payment
                if total != payment.amount :
                    code = HTTPStatus.NOT_ACCEPTABLE
                    raise Exception("The total of the transactions needs to be equals to the payment amount")

            except Exception as exc:
                response = {
                    'status': 'fail',
                    'message': str(exc)
                }

            seller = Account.query.get(payment.receiver_id)
            seller.balance += total

            account.balance -= total
            payment.state = "completed"

            response = {
                'status': 'success',
                'message' : 'The payment was executed'
            }

        else :
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
@payment_controller.route('/payments/<uuid:id>/authorize', methods=['POST'])
@login_required
def authorization_payment(account,id):
    """
        Authorization the payment

        :param payment_id: Id of the payment
        :type payment_id: int

        :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    msg = Message()
    
    if account :

        if account.state:
            try:
                payment = Payment.query.get(id)

                # Check if payments exists
                if not payment:
                    code = HTTPStatus.NOT_FOUND
                    raise Exception("Payment not found")

                if payment.state == "completed":
                    code = HTTPStatus.CONFLICT
                    raise Exception('The payment is already completed')

            except Exception as exc:
                response = {
                    'status': 'fail',
                    'message': str(exc)
                }

            # Let's pretend there is an authorization, and you need to call an "authorization" function, but nothing happens internally.

            response = {
                'status': 'success',
                'message' : 'The payment was authorized'
            }

        else :
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

# Get all the transactions
@payment_controller.route('/payments/<uuid:id>/transactions', methods=['GET'])
@login_required
def get_transactions(account, id):
    """
        Find transactions from payment by ID

        :param id: Id of the payment associated
        :type id: int

        :rtype: dict | bytes (with Transactions)
    """

    code = HTTPStatus.OK
    msg = Message()
    if account:
        
        if account.state:
            try:
                payment = Payment.query.get(id)

                # Check if payments exists
                if not payment:
                    code = HTTPStatus.NOT_FOUND
                    raise Exception("Payment not found")

            except Exception as excep:
                response = {
                    'status': 'fail',
                    'message': str(excep)
                }

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
        else :
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

# Get a specific transaction
@payment_controller.route('/payments/<uuid:id>/transactions/<uuid:transaction>', methods=['GET'])
@login_required
def get_transaction(account, id, transaction):
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
    
    if account:
        
        if account.state:
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

        else :
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
    return msg.message(code,response)