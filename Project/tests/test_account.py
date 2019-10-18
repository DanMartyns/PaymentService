# Project/tests/test_account.py

import uuid
import unittest 
import requests
from server.models import Account
from server.PaymentService import db


def register_user(user_id, password, currency):
    headers = {'Content-Type': "application/json"}    
    data = "{\"user_id\" : \""+str(user_id)+"\",\"currency\" : \""+currency+"\", \"password\" : \""+password+"\"}"
    response = requests.post('http://localhost:5000/account', headers=headers, data=data)
    return response

# def login_user(self, user_id, password):
#     return self.client.post(
#         '/auth/login',
#         data=json.dumps(dict(
#             user_id=user_id,
#             password=password
#         )),
#         content_type='application/json',
#     )


class TestAuth(unittest.TestCase):
    
    def test_registration(self):
        """ Test for user registration """
        user_id = uuid.uuid4()
        password = "my-precious"
        currency = "EUR"

        response = register_user(user_id, password , currency)
        print(response.text)
        data = response.json()['message']
        self.assertEqual(response.json()['code'], 201)
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['auth_token'])
        self.assertTrue(response.headers['Content-Type'] == 'application/json')

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email"""
        
        user_id = uuid.uuid4()

        account = Account(
            user_id = user_id,
            password = "my-precious",
            currency = "EUR"
        )
        db.session.add(account)
        db.session.commit()

        response = register_user(user_id, "my-precious", "EUR")
        print(response)
        data = response.json()['message']
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == 'User already exists. Please Log in.')
        self.assertTrue(response.headers['Content-Type'] == 'application/json')
        self.assertEqual(response.json()['code'], 202)

if __name__ == '__main__':
    unittest.main()