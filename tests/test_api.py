from datetime import datetime
import time
from unittest import TestCase

import pandas as pd
from cbcdb import DBManager

from jsonrpcclient import request, parse, Ok
import logging
import requests

class TestSimplyBookApi(TestCase):

    def _get_auth_token(self):
