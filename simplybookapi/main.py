import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, Union, Callable, List

from jsonrpcclient import Ok, parse, request

import pandas as pd
import requests
from cbcdb import DBManager
from configservice import Config



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

    def get_auth_token(self, api_url: str, api_credentials: Dict[str, Union[str, int]], fail_counter: int = 0) -> dict:
        """
        Requests an access token from the EzyVet API

        Args:
            api_url: URL to the API
            api_credentials: A dict containing all API credentials

        Returns:
            A string containing an access token. Any prior access tokens will be invalidated when a new access token
            is retrieved.

        """
        simply_book_api = Config().get_env('SIMPLY_BOOK_URL', default_value='https://user-api.simplybook.me', data_type_convert='str')
        simply_book_company = Config().get_env('COMPANY_NAME', default_value='petswellness', data_type_convert='str' )
        simply_book_api_key = Config().get_env('SB_API_KEY', error_flag=True)
        response = requests.post(url=f'{simply_book_api}/login',
                                 json=request('getToken', params=(simply_book_company, simply_book_api_key)))

        if response.status_code != 200:
            if fail_counter > 3:
                raise InvalidTokenResponse(response.text)

        else:
            fail_counter += 1
            self.get_auth_token(api_url, api_credentials, fail_counter)

        token = parse(response.json())['result']

        if token:
            current_dt = datetime.utcnow()
            token_save = {'token': token,
                          'create_date': current_dt}
            with open('token_save.pkl', 'wb') as token_file:
                pickle.dump(token_save, token_file)

            return token_save
        raise EmptyTokenError()


class InvalidTokenResponse(requests.exceptions.HTTPError):
    pass


class EmptyTokenError(Exception):
    pass
