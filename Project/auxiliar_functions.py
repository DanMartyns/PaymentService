import datetime
import uuid
from flask import Flask, jsonify, request, Blueprint

class Message:
    def message(self, reason_code, message):
        return jsonify(code = reason_code, message=message)

class Auxiliar:
    
    def validate_uuid(self,value):
        return isinstance(value, uuid.UUID)
