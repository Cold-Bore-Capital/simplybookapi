from datetime import datetime
from simplybookapi import API

api = API()
res = api.get_all_services_available_times(date_from=datetime(2021, 12, 19), date_to=datetime(2021, 12, 31))

a= 0


