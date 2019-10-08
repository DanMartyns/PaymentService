# IMPORTS
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from account_controller import account_controller
from payment_controller import payment_controller
from models import db

import json

# CONFIG
# initialize instance of WSGI application
# act as a central registry
app = Flask(__name__)

# register routes from account_controller
app.register_blueprint(account_controller)

# register routes from payment_controller
app.register_blueprint(payment_controller)


# database
POSTGRES = {
    'user': 'payment',
    'pw': 'payment',
    'db': 'payment',
    'host': '127.0.0.1',
    'port': '5432',
}

DB_URL = 'postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
	db.init_app(app)
	
	#db.drop_all()
	db.create_all()


# ROUTES

# Home
@app.route('/', methods=['GET'])
def home():
	response = {
		'status': 'success'
	}
	return (jsonify(response), 200)
