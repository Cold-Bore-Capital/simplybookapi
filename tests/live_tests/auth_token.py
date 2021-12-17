from simplybookapi.main import Main



m = Main(test_mode=False)
path = m._simply_book_api
api_key = m._simply_book_api_key
company = m._simply_book_company

res = m.get_auth_token(path, company, api_key)

a = 0
