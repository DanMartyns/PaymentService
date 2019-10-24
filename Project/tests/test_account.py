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

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        register_user(user_id, password, currency)
        response = login_user(user_id, password)
        print(response.text)
        auth_token = response.json()['message']['auth_token']
        print('Auth Token :', auth_token)
        headers = {'Content-Type': "application/json", 'Authorization': auth_token}
        data = "{\"amount\" : 20.0}"
        response = requests.post('http://localhost:5000/amount', headers=headers, data=data)
        print(response.text)


if __name__ == '__main__':
    unittest.main()
