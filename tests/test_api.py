from datetime import datetime
import time
from unittest import TestCase

import pandas as pd

from simplybookapi.main import Main


class TestSimplyBookApi(TestCase):

    def test__get_auth_token(self):
        m = Main(test_mode=True)
        m.get_auth_token('', '')
        self.assertEqual(1,1)


