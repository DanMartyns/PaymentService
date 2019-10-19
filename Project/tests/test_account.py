# Project/tests/test_account.py

import uuid
import unittest 
import requests
import json
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

#    def test_registered_with_already_registered_user(self):
#        """ Test registration with already registered email"""
#
#        user_id = uuid.uuid4()
#        account = Account(user_id=user_id, password="my-precious", currency=Currency("EUR"))
#
#        response = register_user(user_id, "my-precious", "EUR")
#        print("Response : ", response)
#        data = response.json()['message']
#        self.assertTrue(data['status'] == 'fail')
#        self.assertTrue(data['message'] == 'User already exists. Please Log in.')
#        self.assertTrue(response.headers['Content-Type'] == 'application/json')
#        self.assertEqual(response.json()['code'], 202)

    def test_login(self):
        """ Test the login """

        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        response = register_user(user_id, password, currency)
        print(user_id)
        response = login_user(user_id, password)
        print("Response : \n", response.text)
        #print(json.dumps(response.json()['message'], indent=4))
        print("Finished test_login")


if __name__ == '__main__':
    unittest.main()
