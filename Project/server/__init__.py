# server/__init__.py

# IMPORTS
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
CORS(app, support_credentials=True)

db = SQLAlchemy()
bcrypt = Bcrypt()

# database
POSTGRES = {
    'user': 'payment',
    'pw': 'payment',
    'db': 'payment',
    'host': '127.0.0.1',
    'port': '5433',
}

DB_URL = 'postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'my_precious')
app.config['BCRYPT_LOG_ROUNDS'] = 13

from server.user_controller import user_controller
from server.account_controller import account_controller
from server.payment_controller import payment_controller

bcrypt.init_app(app)
db.init_app(app)

# register routes from user_controller
app.register_blueprint(user_controller)

# register routes from account_controller
app.register_blueprint(account_controller)

# register routes from payment_controller
app.register_blueprint(payment_controller)

with app.app_context():
    db.drop_all()
    db.engine.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    db.create_all()

app.app_context().push()
# Home
@app.route('/', methods=['GET'])
def home():
    response = {
        'status': 'success'
    }
    return jsonify(response), 200


