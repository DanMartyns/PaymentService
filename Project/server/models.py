# Project/models.py

import uuid
import enum
import jwt
import os
import datetime
from iso4217 import Currency
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
BCRYPT_LOG_ROUNDS = 13


class PaymentState(enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


class TransactionState(enum.Enum):
    created = "created"
    accepted = "accepted"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

# MODELS

class BaseModel(db.Model):
    """
        Base data model for all objects
    """
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def json(self):
        """
            Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value if not isinstance(
                value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }

class Active_Sessions(BaseModel, db.Model):
    """
        Token Model for storing JWT tokens
    """
    __tablename__ = 'active_sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    emission_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.emission_at = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_active_session(auth_token):
        # check whether auth token has been blacklisted
        res = Active_Sessions.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

class Account(BaseModel, db.Model):
    """
        Model for the account table
    """
    __tablename__ = 'account'

    # The account id
    id = db.Column(UUID(as_uuid=True),server_default=db.text("uuid_generate_v4()"), unique=True, primary_key=True)
    # The user id 									
    user_id = db.Column(UUID(as_uuid=True),unique=True, nullable=False) 								
    # The ammount in his account
    balance = db.Column(db.Float, default=0.0, nullable=False)
    # The atual currency
    currency = db.Column(db.Enum(Currency), default=Currency.eur, nullable=False) 
    # The state of the account : active or inactive
    state = db.Column(db.Boolean, default=True, nullable=False)
    # The date when the account was created
    created_at = db.Column(db.DateTime, nullable=False)
    # The date when the information account was updated
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, password, currency):
        self.user_id = user_id
        self.password = bcrypt.generate_password_hash(password, BCRYPT_LOG_ROUNDS).decode()
        self.balance = 0.0
        self.currency = currency
        self.state = True
        self.created_at = self.updated_at = datetime.datetime.utcnow().isoformat()

    def encode_auth_token(self):
        """
            Generates the Auth Token
            :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': str(self.id)
            }
            return jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e
    
    @staticmethod
    def decode_auth_token(auth_token):
        """
            Validates the auth token
            :param auth_token:
            :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            is_active_token = Active_Sessions.check_active_session(auth_token)
            if not is_active_token:
                return 'Token invalid.'
            else:
                return uuid.UUID(uuid.UUID(payload['sub']).hex) 
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

class Payment(BaseModel, db.Model):
    """
        Model for the payment table
    """
    __tablename__ = 'payment'

    # The payment id
    id = db.Column(UUID(as_uuid=True),server_default=db.text("uuid_generate_v4()"), unique=True, primary_key=True)
    # The "product" id
    request_id = db.Column(db.String(40),unique=True)
    # The buyer account
    account_id = db.Column(UUID(as_uuid=True),db.ForeignKey("account.id"), unique=True, nullable=False)
    # The seller account 	
    receiver_id = db.Column(UUID(as_uuid=True),db.ForeignKey("account.id"), unique=True, nullable=False) 	
    # The date when the payment was made
    created_at = db.Column(db.DateTime, nullable=False)
    # The date when the payment was made
    completed_at = db.Column(db.DateTime)
    # The state of the payment
    state = db.Column(db.Enum(PaymentState), nullable=False)
    # The amount who will be paid
    amount = db.Column(db.Float, nullable=False)
    # The currency
    currency = db.Column(db.Enum(Currency), nullable=False) 			
    # An optional textual reference shown on the transaction
    reference = db.Column(db.String(128))

    buyer = db.relationship("Account", foreign_keys=account_id)
    seller = db.relationship("Account", foreign_keys=receiver_id)

    def __init__(self, request_id, account_id, receiver_id, currency, reference):
        self.id = uuid.uuid4()
        self.request_id = request_id
        self.account_id = account_id
        self.receiver_id = receiver_id
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.state = PaymentState.pending
        self.amount = 0.0
        self.currency = currency
        self.reference = reference

class Transaction(BaseModel, db.Model):
    """
        Model for the transactions table
    """
    __tablename__ = 'transaction'

    # The id of the transaction
    id = db.Column(UUID(as_uuid=True),server_default=db.text("uuid_generate_v4()"), primary_key=True)
    # The amount of the transaction
    amount = db.Column(db.Float, nullable=False)
    # Emission date of the transaction
    emission_date = db.Column(db.DateTime, nullable=False)
    # The state of the transaction
    state = db.Column(db.Enum(TransactionState), nullable=False)
    # The update date of the transaction
    update_date = db.Column(db.DateTime, nullable=False)
    # The payment id
    id_payment = db.Column(UUID(as_uuid=True), db.ForeignKey("payment.id"), nullable=False)
    # An optional textual reference shown on the transaction
    reference = db.Column(db.String(128))
    
    payment = db.relationship("Payment", foreign_keys=id_payment)

    def __init__(self, amount, id_payment, reference):
        self.amount = amount
        self.emission_date = datetime.datetime.now()
        self.state = TransactionState.created
        self.update_date = datetime.datetime.now()
        self.id_payment = id_payment
        self.reference = reference
