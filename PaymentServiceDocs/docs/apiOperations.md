# API Operations

## Account

#### Create Account

This endpoint creates one account. 

!!! note
    At the moment of creating an account, an outsourcing already offers a unique identifying ID that identifies the user. You only need to match this ID to an account.

!!! warning 
    If the external source is a social network, for example, a user can sign in with Facebook or Instagram and this generates 2 different users.

##### Request

    POST /account

**Content-Type** : application/json


| Field         | Description                                    | Format                     |
|:-------------:|:---------------------------------------------- |:--------------------------:|
| id            | the account ID                                 | UUID                       |
| user_id       | the user ID                                    | UUID                       |
| type          | the account type                               | Text                       |   
| balance       | the available balance                          | Decimal                    |
| currency      | the account currency                           | 3-letter ISO currency code |
| state         | the account state, one of _active_, _inactive_ | Boolean                    |
| created_at    | the instant when the account was created       | ISO date/time              |
| updated_at    | the instant when the account was last updated  | ISO date/time              |


##### Response 


--------

#### Add Amount

##### Request

    POST /account/<id>/amount

**Content-Type** : application/json


| Field         | Description                                    | Format                     |
|:-------------:|:---------------------------------------------- |:--------------------------:|
| amount        | amount to add to account                       | Decimal                    |

--------

#### Activate Account

##### Request

    POST /account/<id>/activate


**Content-Type** : application/json


| Field         | Description                                    | Format                     |
|:-------------:|:---------------------------------------------- |:--------------------------:|
| state         | the account state, one of _active_, _inactive_ | Boolean                    |

--------

#### Desactivate Account

##### Request

    POST /account/<id>/desactivate


**Content-Type** : application/json

| Field         | Description                                    | Format                     |
|:-------------:|:---------------------------------------------- |:--------------------------:|
| state         | the account state, one of _active_, _inactive_ | Boolean                    |

## Payment

> All incoming and outgoing payments are represented as transactions and are processed in two stages from the user's perspective:

> - a new transaction is created,
> - the created transaction is processed, i.e.
    credit/debit on both sides of transaction if Revolut-to-Revolut, posted to the external payment network (Faster Paymetns, SEPA, SWIFT etc.).

> A new transaction has pending state, and a processed transaction's state can be one of completed, failed, reverted or declined.

#### Create Payment

*This endpoint creates a new payment.*

##### Request

    POST /pay

**Content-Type** : application/json

!!! warning
    To avoid duplicate payment submission because of an error in your code, **request_id** must be unique for each submitted payment. The **request_id** must be previously persisted on your side.


| Field           | Description                                                   | Format                     |
|:-------------:  |:----------------------------------------------                |:--------------------------:|
| request_id	  | the client provided ID of the transaction (40 characters max) |	Text                       |  
| account_id	  | the ID of the account to pay from                             |	UUID                       |
| receiving_id    |	the ID of the receiving account                               |	UUID                       |
| amount          |	the transaction amount                                        |	Decimal                    |
| currency        |	the transaction currency                                      |	3-letter ISO currency code |
| reference       |	an optional textual reference shown on the transaction        | Text                       |

##### Response

| Field         | Description                                                           | Format                     |
|:-------------:|:----------------------------------------------                        | :-------------------------:|
| id            | the ID of the created transaction                                     |	UUID                     |
| state	        | the transaction state: *pending*, *completed*, *declined* or *failed* |	Text                     |
| reason_code   | reason code for *declined* or *failed* transaction state              |	Text                     |
| created_at    | the instant when the transaction was created	                        | ISO date/time              |
| completed_at	| the instant when the transaction was completed                        | ISO date/time              |

#### Receive Payment

*This endpoint receives a payment.*

##### Request

    GET /pay

**Content-Type** : application/json

[No Body]

## Errors

The API uses the following error codes:

|Code|	Meaning|
|---| ---- |
|400|	Bad Request -- Your request is invalid.|
|401|	Unauthorized -- Your API key is wrong.|
|403|	Forbidden -- Access to the requested resource or action is forbidden.|
|404|	Not Found -- The requested resource could not be found.|
|405|	Method Not Allowed -- You tried to access an endpoint with an invalid method.|
|406|	Not Acceptable -- You requested a format that isn't JSON.|
|429|	Too Many Requests -- You're sending too many requests.|
|500|	Internal Server Error -- We had a problem with our server. Try again later.|
|503|	Service Unavailable -- We're temporarily offline for maintenance. Please try again later.|

