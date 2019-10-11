# PaymentService
This is a payment service for the Service Engineering discipline. This service is intended to be generic and reusable, and will be accessed by other students for their own applications.

# Setup

# 1. 

## Create a virtual environment
'''
sudo pip install virtualenv
virtualenv venv --python=python3
source venv/bin/activate
'''

## Install the requirements
'''
pip install -r requirements.pip
'''

## Initiate the Gunicorn
In the file PaymentService.py, you can change the exposed port for the database
'''
gunicorn PaymentService:app -b 0.0.0.0:6000
'''

# 2.

You must install **docker** and **docker-compose**

Into the folder "Project" run the command :
'''
docker-compose up
'''

If you want run the containers in the background, change the command to:
'''
docker-compose up -d
'''

To stop the containers, inside the Project folder, run the command:
'''
docker-compose stop
'''

The documentation is available in : [Documentation](https://danmartyns.github.io/PaymentService/). 
