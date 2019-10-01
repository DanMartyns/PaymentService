from flask import Flask, jsonify, request, Blueprint
from auxiliar_functions import *
import datetime
import uuid

@account_controller.route('/account', methods=['POST'])
def create_account():
    """
        Add an account with a user id

        :rtype: dict | bytes
    """
    try:
        user_id = request.json.get('user_id')
        currency = request.json.get('currency')

        if currency not in currency_codes:
            return status(ERROR)


@user_controller.route('/account/<int:id>/amount', methods=['POST'])
def add_amount(id):
    """
        Add an amount to an account

        :param id: The id of the user to be fetched
	    :type id: int

	    :rtype: dict | bytes
    """

@user_controller.route('/account/<int:id>/activate', methods=['POST'])
def activate_account(id):
    """
        Activate the user account

        :param id: The id of the user to be fetched
	    :type id: int
    
	    :rtype: dict | bytes    
    """

@user_controller.route('/account/<int:id>/desactivate', methods=['POST'])
def desativate_account(id):
    """
        Desactivate the user account

        :param id: The id of the user to be fetched
	    :type id: int
    
	    :rtype: dict | bytes    
    """
