# Project/tests/test_payment.py

import uuid
import unittest
import requests
import json
from iso4217 import Currency
from server import db
from server.models import Payment


def register_user(user_id, password, currency):
    headers = {'Content-Type': "application/json"}
    data = "{\"user_id\" : \""+str(user_id)+"\",\"currency\" : \""+currency+"\", \"password\" : \""+password+"\"}"
    print(data)
    response = requests.post('http://192.168.85-208/account', headers=headers, data=data)
    print(response.text)
    return response


def login_user(user_id, password):
    headers = {'Content-Type': "application/json"}
    data = "{\"user_id\" : \"" + str(user_id) + "\", \"password\" : \"" + password + "\"}"
    response = requests.post('http://192.168.85-208/user/login', headers=headers, data=data)
    print("Login :", response.text)
    return response


class TestAuth(unittest.TestCase):

    def register_user(self):
        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        headers = {'Content-Type': "application/json"}
        data = "{\"user_id\" : \"" + str(user_id) + "\",\"currency\" : \"" + currency + "\", \"password\" : \"" + password + "\"}"
        response = requests.post('http://192.168.85-208/', headers=headers, data=data)
        print(response.text)

    def test_create_payment_with_token(self):
        """ Test the creation of a payment with a token """

        print(" --------------------------- Test 1 - Create Payment ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}
        print("Token : "+auth_token)

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \""+request_id+"\", \"seller_id\" : \""+seller+"\", \"currency\" : \"EUR\"," \
                                                                                 "\"reference\" : \""+reference+"\"} "

        response = requests.post('http://192.168.85-208/payments', headers=headers, data=data)
        print("Payment id "+response.json()['message']['id'])

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

    def test_create_payment_without_token(self):
        """ Test the creation of a payment without a token, that is without login """

        print(" --------------------------- Test 2 - Create Payment ( without token ) ----------------------------")

        headers = {'Content-Type': "application/json"}

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \""+request_id+"\", \"seller_id\" : \""+seller+"\", \"currency\" : \"EUR\"," \
                                                                                 "\"reference\" : \""+reference+"\"} "
        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        self.assertTrue(response.status_code == 401)

    def test_authorization_with_token(self):
        """ Test authorization the payment with a token """

        print(" --------------------------- Test 1 - Authorization ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        payment = response.json()['message']['id']
        print("Payment : "+payment)
        response = requests.post('http://0.0.0.0:5000/payments/'+payment+'/authorize', headers=headers)
        print(response.text)

    def test_create_transaction_with_token(self):
        """ Test the creation of a transaction with a token """

        print(" --------------------------- Test 3 - Create Transaction ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \""+request_id+"\", \"seller_id\" : \""+seller+"\", \"currency\" : \"EUR\"," \
                                                                                 "\"reference\" : \""+reference+"\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \""+reference+"\"}"
        response = requests.post('http://0.0.0.0:5000/payments/'+payment+'/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

    def test_create_transaction_without_token(self):
        """ Test the creation of a transaction without a token """

        print(" --------------------------- Test 3 - Create Transaction ( without token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \""+request_id+"\", \"seller_id\" : \""+seller+"\", \"currency\" : \"EUR\"," \
                                                                                 "\"reference\" : \""+reference+"\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        headers = {'Content-Type': "application/json"}
        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \""+reference+"\"}"
        response = requests.post('http://0.0.0.0:5000/payments/'+payment+'/transactions', headers=headers, data=data)

        self.assertTrue(response.status_code == 401)

    def test_execute_with_token_without_money(self):
        """ Test execute a payment with a token without money """

        print(" --------------------------- Test 3 - Execute payment ( with token ) without money ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Execute Payment ##########################################

        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/execute', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'fail')
        self.assertTrue(response.json()['message']['message'] == 'The account does not have enough available amount')
        self.assertEqual(response.json()['code'], 406)

    def test_execute_with_token_with_money(self):
        """ Test execute a payment with a token with money """

        print(" --------------------------- Test 3 - Execute payment ( with token ) with money ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ################################### Add Money to the buyer account ##########################################

        data = "{\"amount\" : 20.0}"
        response = requests.post('http://192.168.85-208/account/amount', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['message'] == 'The amount was added.')
        self.assertEqual(response.json()['code'], 200)

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Execute Payment ##########################################

        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/execute', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['message'] == 'The payment was executed')
        self.assertEqual(response.json()['code'], 201)

    def test_execute_without_token(self):
        """ Test execute a payment without a token """

        print(" --------------------------- Test 3 - Execute payment ( without token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Execute Payment ##########################################
        headers = {'Content-Type': "application/json"}
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/execute', headers=headers, data=data)

        self.assertTrue(response.status_code == 401)

    def test_get_transactions_with_token(self):
        """ Test get transactions with a token """

        print(" --------------------------- Test 3 - Get Transactions ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Get all Transactions ##########################################
        response = requests.get('http://0.0.0.0:5000/payments/'+payment+'/transactions', headers=headers)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['transactions'])
        self.assertEqual(response.json()['code'], 200)

    def test_get_transactions_without_token(self):

        """ Test get transactions with a token """

        print(" --------------------------- Test 3 - Get Transactions ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Get all Transactions ##########################################
        headers = {'Content-Type': "application/json" }
        response = requests.get('http://0.0.0.0:5000/payments/'+payment+'/transactions', headers=headers)

        self.assertTrue(response.status_code == 401)

    def test_get_transaction_with_token(self):
        """ Test get transaction with a token """

        print(" --------------------------- Test 3 - Get Transaction ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Get a Transaction ##########################################

        transaction = response.json()['message']['id']
        response = requests.get('http://0.0.0.0:5000/payments/'+payment+'/transactions/'+transaction, headers=headers)
        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['transaction'])
        self.assertEqual(response.json()['code'], 200)

    def test_get_transaction_without_token(self):
        """ Test get transaction without a token """

        print(" --------------------------- Test 3 - Get Transaction ( without token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Get a Transaction ##########################################

        transaction = response.json()['message']['id']
        headers = {'Content-Type': "application/json"}
        response = requests.get('http://0.0.0.0:5000/payments/'+payment+'/transactions/'+transaction, headers=headers)
        self.assertTrue(response.status_code == 401)

    def test_get_payments_with_token(self):
        """ Test get payments with a token """

        print(" --------------------------- Test 3 - Get Payments ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Get Payments ##########################################

        response = requests.get('http://0.0.0.0:5000/payments', headers=headers)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['payments'])
        self.assertEqual(response.json()['code'], 200)


    def test_get_payments_without_token(self):
        """ Test get transaction without a token """

        print(" --------------------------- Test 3 - Get Transaction ( without token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################
        headers = {'Content-Type': "application/json"}
        response = requests.get('http://0.0.0.0:5000/payments', headers=headers)
        self.assertTrue(response.status_code == 401)

    def test_get_payments_with_token(self):
        """ Test get payments with a token """

        print(" --------------------------- Test 3 - Get payments ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Get Payments ##########################################

        response = requests.get('http://0.0.0.0:5000/payments', headers=headers)
        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['payments'])
        self.assertEqual(response.json()['code'], 200)

    def test_cancel_transaction_with_token(self):
        """ Test get transaction without a token """

        print(" --------------------------- Test 3 - Cancel Transaction ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Transaction cancel ##########################################

        transaction = response.json()['message']['id']
        response = requests.post('http://0.0.0.0:5000/payments/'+payment+'/transactions/'+transaction+'/cancel', headers=headers)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertEqual(response.json()['code'], 200)

        response = requests.get('http://0.0.0.0:5000/payments/'+payment+'/transactions/'+transaction, headers=headers)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['transaction']['state'] == 'cancelled')
        self.assertEqual(response.json()['code'], 200)

    def test_cancel_transaction_without_token(self):
        """ Test get transaction without a token """

        print(" --------------------------- Test 3 - Cancel Transaction ( without token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        ########################################## Create and Login Buyer ##########################################

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        ########################################## Create Seller ##########################################

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        ########################################## Create Payment ##########################################

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Porto e Lisboa"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \"" + request_id + "\", \"seller_id\" : \"" + seller + "\", \"currency\" : \"EUR\"," \
                                                                                         "\"reference\" : \"" + reference + "\"} "

        response = requests.post('http://0.0.0.0:5000/payments', headers=headers, data=data)

        ########################################## Create Transaction ##########################################

        reference = "Bilhete de ida"
        payment = response.json()['message']['id']
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        response = requests.post('http://0.0.0.0:5000/payments/' + payment + '/transactions', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['id'])
        self.assertEqual(response.json()['code'], 201)

        ########################################## Transaction cancel ##########################################

        transaction = response.json()['message']['id']
        headers = {'Content-Type': "application/json"}
        response = requests.post('http://0.0.0.0:5000/payments/'+payment+'/transactions/'+transaction+'/cancel', headers=headers)

        self.assertTrue(response.status_code == 401)

        headers = {'Content-Type': "application/json", 'Authorization': auth_token}
        response = requests.get('http://0.0.0.0:5000/payments/'+payment+'/transactions/'+transaction, headers=headers)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['transaction']['state'] == 'created')
        self.assertEqual(response.json()['code'], 200)

    def test_authorize_payment(self):
        """ Test the creation of a payment with a token """

        print(" --------------------------- Test 1 - Create Payment ( with token ) ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the buyer
        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])
        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}
        print("Token : "+auth_token)

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        # This user will be the seller user
        seller_info = register_user(user_id, password, currency)

        # String identifying the product
        request_id = "bilhete"

        # A Product Description
        reference = "Bilhete entre Lisboa e Porto para teste"

        # The seller id
        seller = seller_info.json()['message']['account']['id']

        data = "{\"request_id\" : \""+request_id+"\", \"seller_id\" : \""+seller+"\", \"currency\" : \"EUR\"," \
                                                                                 "\"reference\" : \""+reference+"\"} "

        response = requests.post('http://192.168.85-208/payments', headers=headers, data=data)
        payment_id = response.json()['message']['id']

        reference = "Bilhete de ida"
        data = "{\"amount\" : 20.0,\"reference\" : \"" + reference + "\"}"
        requests.post('http://0.0.0.0:5000/payments/' + payment_id + '/transactions', headers=headers, data=data)

        reference = "Bilhete de volta"
        data = "{\"amount\" : 25.0,\"reference\" : \"" + reference + "\"}"
        requests.post('http://0.0.0.0:5000/payments/' + payment_id + '/transactions', headers=headers, data=data)

        auth = requests.post('http://0.0.0.0:5000/payments/'+str(payment_id)+'/authorize', headers=headers)

        print("Authorize " + str(auth.json()))
