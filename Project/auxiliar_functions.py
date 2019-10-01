import urllib, re
import uuid
import datetime
from flask import Flask, jsonify, request, Blueprint

class Message:
    def message(self, reason_code, message):
        return jsonify(code = reason_code, message=message)


class Auxiliar:
    
    def currency_codes(self):
        url = "http://www.iso.org/iso/support/faqs/faqs_widely_used_standards/widely_used_standards_other/currency_codes/currency_codes_list-1.htm"
        return re.findall(r'\<td valign\="top"\>\s+([A-WYZ][A-Z]{2})\s+\</td\>', urllib.request.urlopen(url).read())
    
    def validate_uuid(self,value):
        return isinstance(value, uuid.UUID)
