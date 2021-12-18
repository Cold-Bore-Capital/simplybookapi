import pickle
from datetime import datetime
from typing import Union
import json
import pandas as pd
import requests
from cbcdb import DBManager
from configservice import Config
from jsonrpcclient import request, request_json


class Core:
    """
        Queries the SimplyBook.me API.
        """

    def __init__(self, test_mode=False):
        # In test mode the self._db value will be set externally by the unit test.
        self._db = DBManager() if not test_mode else None
        self.start_time = None
        self._access_token_cache = None
        # Start out with a now expire time
        self._access_token_cache_expire = datetime.now()
        self._set_env_values(test_mode)

    def _set_env_values(self, test_mode):
        self._simply_book_api = Config(test_mode).get_env('SIMPLY_BOOK_URL',
                                                          default_value='https://user-api.simplybook.me',
                                                          test_response='https://abcdefg.com')

        self._simply_book_company = Config(test_mode).get_env('COMPANY_NAME', default_value='petswellness',
                                                              test_response='petswellness')

        self._simply_book_api_key = Config(test_mode).get_env('SB_API_KEY', error_flag=True, test_response='ABCDEFG')

        self._retry_limit = Config(test_mode).get_env('API_RETRY_LIMIT', default_value=3, data_type_convert='int')

        self._token_expire = Config(test_mode).get_env('TOKEN_EXPIRE', default_value=10, data_type_convert='int')

        self._user_login_name = Config(test_mode).get_env('SB_USER_LOGIN_NAME', error_flag=True,
                                                          test_response='ABCDEFG')

        self._user_password = Config(test_mode).get_env('SB_USER_PASSWORD', error_flag=True, test_response='ABCDEFG')

    '''
    # Section - Public Methods
    '''

    def get(self,
            function: str,
            params: Union[tuple, dict, None] = None,
            endpoint: str = None,
            dataframe_flag: bool = False) -> Union[pd.DataFrame, None, list]:
        """
        Main function to get data from API.

        Args:
            endpoint: A string with the endpoint name. i.e 'login', 'bookings'.
            function: The name of the RPC function to call
            params: A tuple containing the parameter inputs to the RPC function.
            dataframe_flag: When set to true, method will return results in a Pandas DataFrame format.

        Returns:
            If dataframe_flag is False: A list of dicts containing the data.
            If dataframe_flag is True: A Pandas DataFrame containing the data.

        """
        token_type = 'user' if endpoint == 'admin' else 'api'
        token = self._get_token(token_type)
        endpoint = endpoint if endpoint else ''
        path = f'{self._simply_book_api}/{endpoint}'
        headers = {'X-Company-Login': self._simply_book_company}
        if token_type == 'api':
            headers['X-Token'] = token
        else:
            headers['X-User-Token'] = token
        output = self._sb_api_query(path, function, params, headers)
        if dataframe_flag:
            if output:
                return pd.DataFrame(output)
            else:
                return None
        return output

    def _sb_api_query(self,
                      path: str,
                      function: str,
                      params: tuple,
                      headers: dict = None,
                      fail_counter: int = 0) -> Union[dict, list, str]:
        """
        Queries the SB API and handles error retries.

        Args:
            path: The full path to the API end point. For example, https://user-api.simplybook.me/login
            function: The name of the RPC function to call
            params: A tuple or dict containing the values to pass in to the RPC.
            headers: Authentication or other headers to send.
            fail_counter: A counter to track the number of failed API query events.

        Returns:
            The decoded data from the API response as either a list or dict.
        """
        if isinstance(params, dict):
            # Convert the params into a list/dict. The RPC function requires that even a dict type structure
            # be wrapped in a list.
            params = [params]
        response = requests.post(url=path, json=request(function, params=params), headers=headers)
        if response.status_code != 200:
            if response.status_code == 500:
                error = 'Server error - 500 Code'
                raise SBAPIError(error)
            if fail_counter > self._retry_limit:
                raise InvalidTokenResponse(response.text)
            else:
                print(
                    f'API query failed with error code {response.status_code}. Retry number {fail_counter}.\n{response.text}')
                fail_counter += 1
                self._sb_api_query(path, function, params, headers, fail_counter)
        data = response.json()
        if 'error' in data.keys():
            raise SBAPIError(data['error'])
        else:
            return data['result']

    def _get_token(self, token_type: str) -> str:
        """
        Requests an API type access token from the Simply Book API

        Returns an application's token string for a company. You should use this token to authenticate all calls of
        Company public service methods, Company public service API methods, and Catalogue|Catalogue API methods.

        Args:
            token_type: Either 'api', or 'user'. This will switch between reading the file token_save.pkl for API and
                        user_token_save.pkl for user.

        Returns:
            A string containing an access token. Any prior access tokens will be invalidated when a new access token
            is retrieved.

        """
        api_path = self._simply_book_api
        company = self._simply_book_company
        api_key = self._simply_book_api_key
        user_login_name = self._user_login_name
        user_password = self._user_password
        token = self._read_token_pickle(self._token_expire, token_type)
        if not token:
            path = f'{api_path}/login'
            if token_type == 'api':
                params = (company, api_key)
                function = 'getToken'
                token_file_path = '../token_save.pkl'
            elif token_type == 'user':
                params = (company, user_login_name, user_password)
                function = 'getUserToken'
                token_file_path = '../user_token_save.pkl'
            else:
                raise InvalidTokenTypeSelection(token_type)

            token = self._sb_api_query(path, function, params)
            if token:
                current_dt = datetime.utcnow()
                token_save = {'token': token,
                              'create_date': current_dt}
                with open(token_file_path, 'wb') as token_file:
                    pickle.dump(token_save, token_file)
                return token
            else:
                raise EmptyTokenError()
        else:
            return token

    # def _get_user_token(self) -> str:
    #     """
    #     Requests an User type access token from the Simply Book API
    #
    #     Returns an authentication token string. You should use this token to authenticate all calls of
    #     Company administration service methods, Company administration service API methods.
    #     and Catalogue API methods
    #
    #     Args:
    #
    #     Returns:
    #         A string containing an access token. Any prior access tokens will be invalidated when a new access token
    #         is retrieved.
    #
    #     """
    #     api_path = self._simply_book_api
    #     company = self._simply_book_company
    #     user_login_name = self._user_login_name
    #     user_password = self._user_password
    #     token = self._read_token_pickle(self._token_expire, 'user')
    #     if not token:
    #         path = f'{api_path}/login'
    #         params = (company, user_login_name, user_password)
    #         function = 'getUserToken'
    #         token = self._sb_api_query(path, function, params)
    #         if token:
    #             current_dt = datetime.utcnow()
    #             token_save = {'token': token,
    #                           'create_date': current_dt}
    #             with open('../user_token_save.pkl', 'wb') as token_file:
    #                 pickle.dump(token_save, token_file)
    #             return token
    #         else:
    #             raise EmptyTokenError()
    #     else:
    #         return token

    @staticmethod
    def _read_token_pickle(token_expire_limit: int, token_type: str) -> Union[str, bool]:
        """
        Reads the locally saved token from pickle. Returns the token if not past expire time, otherwise returns false.

        Args:
            token_expire_limit: The number of minutes from token create date before the token becomes invalid.
            token_type: Either 'api', or 'user'. This will switch between reading the file token_save.pkl for API and
                        user_token_save.pkl for user.

        Returns:
            Either a token, or False.
        """
        filename = '../token_save.pkl' if token_type == 'api' else '../user_token_save.pkl'
        try:
            with open(filename, 'rb') as token_file:
                token_data = pickle.load(token_file)
                token_create_time = token_data['create_date']
                now_time = datetime.utcnow()
                token_age = (now_time - token_create_time).seconds / 60
                if token_age > token_expire_limit:
                    return False
                else:
                    return token_data['token']
        except:
            return False


class InvalidTokenResponse(requests.exceptions.HTTPError):
    pass


class EmptyTokenError(Exception):
    pass


class SBAPIError(Exception):
    pass


class PickleNotFoundError(Exception):
    pass


class InvalidTokenTypeSelection(Exception):
    def __init__(self, token_type):
        super().__init__(f'Invalid token type specified. You specified {token_type}. Valid types are "api" or "user"')
