from datetime import datetime
from simplybookapi.functions.admin.get_bookings import GetBookings

g = GetBookings(test_mode=False)

res = g.get_bookings(date_from=datetime(2021,1,1), date_to=datetime(2021,12,31))

a = 0