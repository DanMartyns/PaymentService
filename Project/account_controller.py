from flask import Flask, jsonify, request, Blueprint
from auxiliar_functions import Auxiliar, Message
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
    
    code = HTTPStatus.OK
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
    

    # Return the information
    date = datetime.datetime.utcnow().isoformat()
    return msg.message(code, jsonify(id=uuid.uuid4(),user_id=user_id,balance=0,currency=currency,state="activate", created_at=date, updated_at=date))



@account_controller.route('/account/<int:id>/amount', methods=['POST'])
def add_amount(id):
    """
        Add an amount to an account

        :param id: The id of the user to be fetched
	    :type id: int

	    :rtype: dict | bytes
    """

@account_controller.route('/account/<int:id>/activate', methods=['POST'])
def activate_account(id):
    """
        Activate the user account

        :param id: The id of the user to be fetched
	    :type id: int
    
	    :rtype: dict | bytes    
    """

@account_controller.route('/account/<int:id>/desactivate', methods=['POST'])
def desativate_account(id):
    """
        Desactivate the user account

        :param id: The id of the user to be fetched
	    :type id: int
    
	    :rtype: dict | bytes    
    """
