
import urllib, re

class Message:
    def __init__(self):


class Auxiliar:
    
    def currency_codes(self):
        url = "http://www.iso.org/iso/support/faqs/faqs_widely_used_standards/widely_used_standards_other/currency_codes/currency_codes_list-1.htm"
        return re.findall(r'\<td valign\="top"\>\s+([A-WYZ][A-Z]{2})\s+\</td\>', urllib.urlopen(url).read())
