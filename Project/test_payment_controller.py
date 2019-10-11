import requests
import uuid
import json

headers = {'Content-Type': "application/json",}


print("************ Generate a Buyer Account ****************")

# Generate the buyer account
data  = "{\"user_id\" : \""+str(uuid.uuid4())+"\",\"currency\" : \"EUR\"}"
response = requests.post('http://0.0.0.0:5000/account', headers=headers, data=data)

buyer = response.json()['message']['account']['id']
print("Buyer number : ",buyer)
print()



print("************ Generate a Seller Account ****************")

# Generate the seller account
data  = "{\"user_id\" : \""+str(uuid.uuid4())+"\",\"currency\" : \"EUR\"}"
response = requests.post('http://0.0.0.0:5000/account', headers=headers, data=data)

seller = response.json()['message']['account']['id']
print("Seller number : ",seller)
print()


print("************ Put Money in Buyer's Account ****************")
# Put money in the buyer's account
data  = "{\"amount\" : 45.0}"
response = requests.post('http://0.0.0.0:5000/account/'+buyer+'/amount', headers=headers, data=data)

# Get the buyer account information to check if the money comes in
response = requests.get('http://0.0.0.0:5000/account/'+buyer)

print("Account balance of the Buyer after put the money:",response.json()['message']['account']['balance'])
print()



print("************ Create a payment ****************")
# Create a payment
request_id = "bilhete" # String identificating the product
reference = "Bilhete entre Porto e Lisboa" # A Product Description 
data  = "{\"request_id\" : \""+request_id+"\",\"buyer_id\" : \""+buyer+"\",\"seller_id\" : \""+seller+"\",\"currency\" : \"EUR\",\"reference\" : \""+reference+"\"}"
response = requests.post('http://0.0.0.0:5000/payment', headers=headers, data=data)

payment = response.json()['message']['id']
print("Payment id : ",payment)
print()

print("************ Check the payments of the Buyer ****************")
# Check the payments of the buyer
response = requests.get('http://0.0.0.0:5000/account/'+buyer+'/payments')
print(json.dumps(response.json()['message']['payments'], indent=4))
print()

print("************ Create a Transaction (bilhete de ida) ****************")
# Create a transaction
reference = "Bilhete de ida"
data  = "{\"amount\" : 20.0,\"reference\" : \""+reference+"\"}"
response = requests.post('http://0.0.0.0:5000/payment/'+payment+'/transactions', headers=headers, data=data)

ida = response.json()['message']['id']
print("Transaction id : ", ida)
print()

print("************ Check the transacction (ida) ****************")
# Check the payments of the buyer
response = requests.get('http://0.0.0.0:5000/payment/'+payment+'/transactions/'+ida)
print(json.dumps(response.json()['message']['transaction'], indent=4))
print()

print("************ Create a Transaction (bilhete de volta) ****************")
# Create a transaction
reference = "Bilhete de volta"
data  = "{\"amount\" : 20.0,\"reference\" : \""+reference+"\"}"
response = requests.post('http://0.0.0.0:5000/payment/'+payment+'/transactions', headers=headers, data=data)

volta = response.json()['message']['id']
print("Transaction id : ", volta)
print()

print("************ Check the transacction (volta) ****************")
# Check the payments of the buyer
response = requests.get('http://0.0.0.0:5000/payment/'+payment+'/transactions/'+volta)
print(json.dumps(response.json()['message']['transaction'], indent=4))
print()

print("************ Get all the Transactions of a Payment ****************")
# Get all the transactions
response = requests.get('http://0.0.0.0:5000/payment/'+payment+'/transactions', headers=headers)
for eachone in response.json()['message']['transactions']:
	print(json.dumps(eachone, indent=4))
print()

print("************ Cancel a Transaction (bilhete de volta) ****************")
# Cancel a Transaction
response = requests.post('http://0.0.0.0:5000/payment/'+payment+'/transactions/'+volta+'/cancel', headers=headers)
print(response.text)
print()

print("************ Get all the Transactions of a Payment (after cancel one) ****************")
# Get all the transactions
response = requests.get('http://0.0.0.0:5000/payment/'+payment+'/transactions', headers=headers)
for eachone in response.json()['message']['transactions']:
	print(json.dumps(eachone, indent=4))
print()

print("************ Execute a Payment (Bilhete) ****************")
# Execute a Payment
response = requests.post('http://0.0.0.0:5000/payment/'+payment+'/execute', headers=headers)
print(response.text)
print()


print("************ Check the payments of the Buyer (after execute the payment) ****************")
# Check the payments of the buyer
response = requests.get('http://0.0.0.0:5000/account/'+buyer+'/payments')
print(json.dumps(response.json()['message']['payments'], indent=4))
print()

print("************ Check the Buyer account (after execute the payment) ****************")
# Get the buyer account information to check if the money comes in
response = requests.get('http://0.0.0.0:5000/account/'+buyer)

print("Account balance of the Buyer after put the money:",response.json()['message']['account']['balance'])
print()
