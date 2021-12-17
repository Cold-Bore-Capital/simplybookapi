import pickle
from datetime import datetime, timedelta
from typing import Any, Union, Tuple

import pandas as pd
import requests
from cbcdb import DBManager
from configservice import Config
from jsonrpcclient import request


class Main:
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

    '''
    # Section - Public Methods
    '''

    def get(self,
            location_id: int,
            endpoint_ver: str,
            endpoint_name: str,
            params: dict = None,
            headers: dict = None,
            dataframe_flag: bool = False) -> Union[pd.DataFrame, None, list]:
        """
        Main function to get api data
        Args:
            location_id: Location ID to operate on.
            endpoint_name: endpoint to query
            endpoint_ver: version of the endpoint to use.
            headers: headers to dict format
            params: params to dict format
            dataframe_flag: When set to true, method will return results in a Pandas DataFrame format.

        Returns:
            If dataframe_flag is False: A list of dicts containing the data.
            If dataframe_flag is True: A Pandas DataFrame containing the data.
        """
        endpoint = f'{endpoint_ver}/{endpoint_name}'
        db = self._db
        params = self._build_params(params)
        if not self._access_token_cache or self._access_token_cache_expire <= datetime.now():
            api_credentials = self._get_api_credentials(location_id, self._config.ezy_vet_api, db,
                                                        self.get_access_token, 10)
            self._access_token_cache_expire = datetime.now() + timedelta(minutes=10)
            self._access_token_cache = api_credentials
        else:
            api_credentials = self._access_token_cache
        headers = self._set_headers(api_credentials, headers)
        api_url = self._config.ezy_vet_api
        output = self._get_data_from_api(api_url=api_url,
                                         params=params,
                                         headers=headers,
                                         endpoint=endpoint,
                                         db=db,
                                         location_id=location_id)
        if dataframe_flag:
            if output:
                return pd.DataFrame(output)
            else:
                return None
        return output

    def get_auth_token(self, api_path, company, api_key, fail_counter: int = 0) -> dict:
        """
        Requests an access token from the EzyVet API

        Args:
            api_url: URL to the API
            api_credentials: A dict containing all API credentials

        Returns:
            A string containing an access token. Any prior access tokens will be invalidated when a new access token
            is retrieved.

        """
        token = self._read_token_pickle(self._token_expire)
        if not token:
            path = f'{api_path}/login'
            params = (company, api_key)
            function = 'getToken'
            token = self._sb_api_query(path, function, params)
            if token:
                current_dt = datetime.utcnow()
                token_save = {'token': token,
                              'create_date': current_dt}
                with open('../token_save.pkl', 'wb') as token_file:
                    pickle.dump(token_save, token_file)
                return token
            else:
                raise EmptyTokenError()
        else:
            return token

    def _sb_api_query(self, path: str, function: str, params: Tuple[Any], fail_counter: int = 0) -> Union[dict, list]:
        """
        Queries the SB API and handles error retries.

        Args:
            path: The full path to the API end point. For example, https://user-api.simplybook.me/login
            function: The name of the RPC function to call
            params: A tuple containing the values to pass in to the RPC.
            fail_counter: A counter to track the number of failed API query events.

        Returns:
            The decoded data from the API response as either a list or dict.
        """
        response = requests.post(url=path, json=request(function, params=params))
        if response.status_code != 200:
            if fail_counter > self._retry_limit:
                raise InvalidTokenResponse(response.text)
            else:
                print(
                    f'API query failed with error code {response.status_code}. Retry number {fail_counter}.\n{response.text}')
                fail_counter += 1
                self._sb_api_query(path, function, params, fail_counter)
        data = response.json()
        if 'error' in data.keys():
            raise SBAPIError(data['error'])
        else:
            return data['result']

    @staticmethod
    def _read_token_pickle(token_expire_limit: int) -> Union[str, bool]:
        """
        Reads the locally saved token from pickle. Returns the token if not past expire time, otherwise returns false.

        Args:
            token_expire_limit: The number of minutes from token create date before the token becomes invalid.

        Returns:
            Either a token, or False.
        """
        try:
            with open('../token_save.pkl', 'rb') as token_file:
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
