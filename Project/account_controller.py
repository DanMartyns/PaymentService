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
        if aux.validate_uuid(user_id):
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your user_id is wrong. The user_id is not a universally unique identifier" )
        elif currency not in aux.currency_codes():
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your currency is wrong. Uses the international standard that defines three-letter codes as currencies established by the International Organization. (ISO 4217)" )

    except Exception as excep :
        return msg.message(code,str(excep))

    # Save the account with the user id
    account = Account(user_id = user_id,currency = currency)
    db.session.add(account)
    db.session.commit()

    # Return the information
    date = datetime.datetime.utcnow().isoformat()
    return msg.message(code, jsonify(id=uuid.uuid4(),user_id=user_id,balance=0,currency=currency,state="activate", created_at=date, updated_at=date))



@account_controller.route('/account/<int:account_id>/amount', methods=['POST'])
def add_amount(account_id):
    """
        Add an amount to an account

        :param id: The id of the user to be fetched
	    :type id: int

	    :rtype: dict | bytes
    """

    code = HTTPStatus.OK
    aux = Auxiliar()
    msg = Message()

    try : 
        # Get parameters
        amount = request.json.get('amount')

        # Flag to check if account exists
        exists = db.Query(Account).filter_by(Account.id.contains(account_id))
        print(exists)

        #Flag to check if the account is activated
        activated = db.Query(Account).filter_by(Account.state == True)

        # Validate the parameters 
        if aux.validate_uuid(account_id) and not exists: 
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your number account is wrong. The number account is not a universally unique identifier or doesn't exist" )
        elif not activated:
            code = HTTPStatus.METHOD_NOT_ALLOWED
            raise Exception("Your number account is desactivated." )            
        elif not isinstance(float(amount), float):
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your amount is wrong. The amount is not valid" )
        elif float(amount) < 0.0 :
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your amount is wrong. The amount needs to be more than 0.0" )

    except Exception as excep :
        return msg.message(code,str(excep))

    # Update the total amount in his account
    db.update(Account).values(balance = amount).where(id == account_id)
    db.commit()

    return msg.message(code,'Your amount was added')



@account_controller.route('/account/<int:account_id>/activate', methods=['POST'])
def activate_account(account_id):
    """
        Activate the user account

        :param id: The id of the user to be fetched
	    :type id: int
    
	    :rtype: dict | bytes    
    """
    
    code = HTTPStatus.OK
    aux = Auxiliar()
    msg = Message()

    try : 
        # Flag to check if account exists
        exists = db.Query(Account).filter_by(Account.id.contains(account_id))
        print(exists)

        #Flag to check if the account is activated
        activated = db.Query(Account).filter_by(Account.state == True)        

        # Validate the parameters 
        if aux.validate_uuid(account_id) and not exists: 
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your number account is wrong. The number account is not a universally unique identifier or doesn't exist" )
        elif activated:
            code = HTTPStatus.NOT_MODIFIED
            raise Exception("The account is already activated")
    except Exception as excep :
        return msg.message(code,str(excep))

    # Update the state of the account
    db.update(Account).values(state = True).where(id == account_id)
    db.commit()

    return msg.message(code,'Your account is activated')

@account_controller.route('/account/<int:account_id>/desactivate', methods=['POST'])
def desativate_account(account_id):
    """
        Desactivate the user account

        :param id: The id of the user to be fetched
	    :type id: int
    
	    :rtype: dict | bytes    
    """
    code = HTTPStatus.OK
    aux = Auxiliar()
    msg = Message()

    try : 
        # Flag to check if account exists
        exists = db.Query(Account).filter_by(Account.id.contains(account_id))
        print(exists)

        #Flag to check if the account is activated
        activated = db.Query(Account).filter_by(Account.state == True)        

        # Validate the parameters 
        if aux.validate_uuid(account_id) and not exists: 
            code = HTTPStatus.BAD_REQUEST
            raise Exception("Your number account is wrong. The number account is not a universally unique identifier or doesn't exist" )
        elif not activated:
            code = HTTPStatus.NOT_MODIFIED
            raise Exception("The account is already desactivated")
    except Exception as excep :
        return msg.message(code,str(excep))

    # Update the total amount in his account
    db.update(Account).values(state = False).where(id == account_id)
    db.commit()

    return msg.message(code,'Your account is desactivated')