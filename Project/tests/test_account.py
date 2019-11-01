# Project/tests/test_account.py

import uuid
import unittest 
import requests
import json
from iso4217 import Currency
from server import db
from server.models import Account


def register_user(user_id, password, currency):
    headers = {'Content-Type': "application/json"}    
    data = "{\"user_id\" : \""+str(user_id)+"\",\"currency\" : \""+currency+"\", \"password\" : \""+password+"\"}"
    response = requests.post('http://localhost:5000/account', headers=headers, data=data)
    return response


def login_user(user_id, password):
    headers = {'Content-Type': "application/json"}
    data = "{\"user_id\" : \"" + str(user_id) + "\", \"password\" : \"" + password + "\"}"
    response = requests.post('http://localhost:5000/login', headers=headers, data=data)
    return response


class TestAuth(unittest.TestCase):

    def test_registration(self):
        """ Test for user registration """

        print(" --------------------------- Test 1 - Registration ----------------------------")
        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        response = register_user(user_id, password, currency)
        data = response.json()['message']
        self.assertEqual(response.json()['code'], 201)
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(response.headers['Content-Type'] == 'application/json')
        print(json.dumps(data, indent=4))

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email"""

        print(" ------------ Test 2 - Registration an user already registed ------------------")

        user_id = uuid.uuid4()
        account = Account(user_id=user_id, password="my-precious", currency=Currency("EUR"))
        db.session.add(account)
        db.session.commit()

        response = register_user(user_id, "my-precious", "EUR")
        data = response.json()['message']
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == 'User already exists. Please Log in')
        self.assertTrue(response.headers['Content-Type'] == 'application/json')
        self.assertEqual(response.json()['code'], 202)

    def test_login(self):
        """ Test the login """

        print(" --------------------------- Test 3 - Login ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        register_user(user_id, password, currency)
        response = login_user(user_id, password)
        data = response.json()['message']
        self.assertEqual(response.json()['code'], 200)
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully logged in.')

    def test_access_methods_without_token(self):
        """ Test access to methods without token """

        print(" --------------------------- Test 4 - Try Access without token ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        register_user(user_id, password, currency)

        headers = {'Content-Type': "application/json"}
        data = "{\"amount\" : 20.0}"
        response = requests.post('http://localhost:5000/amount', headers=headers, data=data)
        print(response.text)

    def test_access_methods_with_token(self):
        """ Test access to methods with token """

        print(" --------------------------- Test 5 - Try Access with token ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])

        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}
        data = "{\"amount\" : 20.0}"
        response = requests.post('http://localhost:5000/account/amount', headers=headers, data=data)

        self.assertTrue(response.json()['message']['status'] == 'success')
        self.assertTrue(response.json()['message']['message'] == 'The amount was added.')
        self.assertEqual(response.json()['code'], 200)

    def test_access_account_info_with_token(self):
        """ Test access to info account with token """

        print(" --------------------------- Test 6 - Access Account Information ----------------------------")

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        register_user(user_id, password, currency)
        response = login_user(user_id, password)

        self.assertTrue(response.json()['message']['auth_token'])

        auth_token = response.json()['message']['auth_token']
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}

        data = "{\"amount\" : 20.0}"
        requests.post('http://localhost:5000/account/amount', headers=headers, data=data)
        requests.post('http://localhost:5000/account/amount', headers=headers, data=data)
        requests.post('http://localhost:5000/account/amount', headers=headers, data=data)

        # Get the buyer account information to check if the money comes in
        response = requests.get('http://0.0.0.0:5000/account', headers=headers)
        print(json.dumps(response.json()['message'], indent=4))


if __name__ == '__main__':
    unittest.main()
