from datetime import datetime, timedelta
import time, pickle, os
from unittest import TestCase
from typing import Any, Union, Tuple
from configservice import Config

import pandas as pd

from simplybookapi.main import Main, EmptyTokenError, InvalidTokenResponse


class TestSimplyBookApi(TestCase):

    def test__read_token_pickle(self):
        # Make a pickle first
        current_dt = datetime.utcnow()
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = Main(test_mode=True)
        token = m._read_token_pickle(10)
        golden = 'abcdefg'
        self.assertEqual(golden, token)

        current_dt = datetime.utcnow() - timedelta(minutes=12)
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = Main(test_mode=True)
        token = m._read_token_pickle(10)
        self.assertFalse(token)

        os.remove('../token_save.pkl')
        m = Main(test_mode=True)
        token = m._read_token_pickle(10)
        self.assertFalse(token)

    def test_get_auth_token(self):
        # Make a pickle first
        current_dt = datetime.utcnow()
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = MockAuthToken(test_mode=True)
        token = m.get_auth_token('abc', 'def', 'abc123')
        golden = 'abcdefg'
        self.assertEqual(golden, token)

        current_dt = datetime.utcnow() - timedelta(minutes=12)
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = MockAuthToken(test_mode=True)
        token = m.get_auth_token('abc', 'def', 'abc123')
        golden = 'new_token_res'
        self.assertEqual(golden, token)

        os.remove('../token_save.pkl')
        m = MockAuthToken(test_mode=True)
        token = m.get_auth_token('abc', 'def', 'abc123')
        golden = 'new_token_res'
        self.assertEqual(golden, token)

        with self.assertRaises(EmptyTokenError) as e:
            os.remove('../token_save.pkl')
            m = MockAuthToken(test_mode=True)
            m.fail_mode = True
            token = m.get_auth_token('abc', 'def', 'abc123')



class MockAuthToken(Main):

    def __init__(self, test_mode=True):
        super().__init__(test_mode)
        self.fail_mode = False

    def _sb_api_query(self, path: str, function: str, params: Tuple[Any], fail_counter: int = 0):
        if self.fail_mode:
            return {'result': ''} # Is this really what a bad result looks like?
        else:
            return {'result':'new_token_res'}