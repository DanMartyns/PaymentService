import uuid
from flask import jsonify

class Message:
    @staticmethod
    def message(self, reason_code, message):
        return jsonify(code = reason_code, message=message)

class Auxiliar:
    @staticmethod
    def validate_uuid(self,value):
        return isinstance(value, uuid.UUID)
