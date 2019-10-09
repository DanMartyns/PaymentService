import uuid
import enum
import datetime
from iso4217 import Currency
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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


class Account(BaseModel, db.Model):
    """
            Model for the account table
    """
    __tablename__ = 'account'

    # The account id
    id = db.Column(db.Integer, primary_key=True)
    # The user id 									
    user_id = db.Column(db.Integer, nullable=False) 								
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

    def __init__(self, user_id, currency):
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.balance = 0.0
        self.currency = currency
        self.state = True
        self.created_at = self.updated_at = datetime.datetime.utcnow().isoformat()


class Payment(BaseModel, db.Model):
    """
        Model for the payment table
    """
    tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    # The transaction id
    request_id = db.Column(db.String(40), primary_key=True)
    # The buyer account
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"),nullable=False)
    # The seller account 	
    receiver_id = db.Column(db.Integer, db.ForeignKey("account.id"),nullable=False) 	
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

    def __init__(self, request_id, account_id, receiver_id, amount, currency, reference):
        self.id = uuid.uuid4()
        self.request_id = request_id
        self.account_id = account_id
        self.receiver_id = receiver_id
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.state = PaymentState.pending
        self.amount = amount
        self.currency = currency
        self.reference = reference


class Transaction(BaseModel, db.Model):
    """
            Model for the transactions table
    """
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    emission_date = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.Enum(TransactionState), nullable=False)
    update_date = db.Column(db.DateTime, nullable=False)
    id_payment = db.Column(db.Integer, db.ForeignKey("payment.id"), nullable=False)
    
    payment = db.relationship("Payment", foreign_keys=id_payment)

    def __init__(self, amount, id_payment):
        self.amount = amount
        self.emission_date = datetime.datetime.now()
        self.state = TransactionState.created
        self.update_date = datetime.datetime.now()
        self.id_payment = id_payment
