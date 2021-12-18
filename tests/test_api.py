from datetime import datetime, timedelta
import pickle, os
from unittest import TestCase
from typing import Any, Union, Tuple

from simplybookapi.core import Core, EmptyTokenError, InvalidTokenResponse


class TestSimplyBookApi(TestCase):

    def test__read_token_pickle(self):
        # Make a pickle first
        current_dt = datetime.utcnow()
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = Core(test_mode=True)
        token = m._read_token_pickle(10, 'api')
        golden = 'abcdefg'
        self.assertEqual(golden, token)

        current_dt = datetime.utcnow() - timedelta(minutes=12)
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = Core(test_mode=True)
        token = m._read_token_pickle(10, 'api')
        self.assertFalse(token)

        os.remove('../token_save.pkl')
        m = Core(test_mode=True)
        token = m._read_token_pickle(10, 'api')
        self.assertFalse(token)

    def test_get_auth_token(self):
        # Make a pickle first
        current_dt = datetime.utcnow()
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = MockAuthToken(test_mode=True)
        token = m._get_token('api')
        golden = 'abcdefg'
        self.assertEqual(golden, token)

        current_dt = datetime.utcnow() - timedelta(minutes=12)
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = MockAuthToken(test_mode=True)
        token = m._get_token('api')
        golden = 'new_token_res'
        self.assertEqual(golden, token)

        os.remove('../token_save.pkl')
        m = MockAuthToken(test_mode=True)
        token = m._get_token('api')
        golden = 'new_token_res'
        self.assertEqual(golden, token)

        with self.assertRaises(EmptyTokenError) as e:
            os.remove('../token_save.pkl')
            m = MockAuthToken(test_mode=True)
            m.fail_mode = True
            token = m._get_token('api')

    def test_get_auth_token_user(self):
        # Make a pickle first
        current_dt = datetime.utcnow()
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../user_token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = MockAuthToken(test_mode=True)
        token = m._get_token('user')
        golden = 'abcdefg'
        self.assertEqual(golden, token)

        current_dt = datetime.utcnow() - timedelta(minutes=12)
        token_save = {'token': 'abcdefg',
                      'create_date': current_dt}
        with open('../user_token_save.pkl', 'wb') as token_file:
            pickle.dump(token_save, token_file)

        m = MockAuthToken(test_mode=True)
        token = m._get_token('user')
        golden = 'new_token_res'
        self.assertEqual(golden, token)

        os.remove('../user_token_save.pkl')
        m = MockAuthToken(test_mode=True)
        token = m._get_token('user')
        golden = 'new_token_res'
        self.assertEqual(golden, token)

        with self.assertRaises(EmptyTokenError) as e:
            os.remove('../user_token_save.pkl')
            m = MockAuthToken(test_mode=True)
            m.fail_mode = True
            token = m._get_token('user')



class MockAuthToken(Core):

    def __init__(self, test_mode=True):
        super().__init__(test_mode)
        self.fail_mode = False

    def _sb_api_query(self, path: str, function: str, params: Tuple[Any], fail_counter: int = 0):
        if self.fail_mode:
            return '' # Is this really what a bad result looks like?
        else:
            return 'new_token_res'