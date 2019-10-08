import uuid
import enum
import datetime
from iso4217 import Currency
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PaymentState(enum.Enum):
	pending = "pending"
	completed = "completed"
	failed = "failed"
	declined = "declined"

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
			column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
			for column, value in self._to_dict().items()
		}


class Account(BaseModel, db.Model):
	"""
		Model for the account table
	"""
	__tablename__ = 'account'

	id = db.Column(db.Integer, primary_key=True) 									# The account id
	user_id = db.Column(db.Integer, nullable=False) 								# The user id
	balance = db.Column(db.Float, default=0.0,nullable=False) 						# The ammount in his account
	currency = db.Column(db.Enum(Currency), default= Currency.eur , nullable=False) # The atual currency
	state = db.Column(db.Boolean, default=True, nullable=False) 					# The state of the account : active or inactive
	created_at = db.Column(db.DateTime, nullable=False) 							# The date when the account was created
	updated_at = db.Column(db.DateTime, nullable=False) 							# The date when the information account was updated

	def __init__(self,user_id,currency):
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

	request_id = db.Column(db.String(40), primary_key=True) 			# The transaction id
	buyer_id = db.Column(db.Integer, db.ForeignKey("account.id")) 		# The buyer account
	seller_id = db.Column(db.Integer, db.ForeignKey("account.id")) 		# The seller account
	created_at = db.Column(db.DateTime, nullable=False) 				# The date when the payment was made
	completed_at = db.Column(db.DateTime) 								# The date when the payment was made
	state = db.Column(db.Enum(PaymentState), nullable=False) 			# The state of the payment
	amount = db.Column(db.Float, nullable=False) 						# The amount who will be paid
	currency = db.Column(db.Enum(Currency), nullable=False) 			# The currency 
	reference = db.Column(db.String(128)) 								# An optional textual reference shown on the transaction

	def __init__(self,request_id,buyer_id,seller_id,amount,currency,reference):
		self.request_id = request_id
		self.buyer_id = buyer_id
		self.seller_id = seller_id
		self.created_at = datetime.datetime.utcnow().isoformat()		
		self.state = PaymentState.pending
		self.amount = amount
		self.currency = currency
		self.reference = reference
