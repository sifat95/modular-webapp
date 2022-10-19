import os
import json
from pickle import NONE
from spellchecker import SpellChecker

from django.templatetags.static import static
from pathlib import Path
from django.http import HttpResponse
from google.protobuf.json_format import MessageToJson
from .utils import *

class BillingInterface:
    def __init__(self):
        self.spell = SpellChecker()
    
    def check_limit(api_limit):
        hit_count = api_limit.limit
        if hit_count >= 1000:
            return HttpResponse("API LIMIT")
        else:
            return True