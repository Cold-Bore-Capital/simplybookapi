from datetime import datetime
from simplybookapi import API

api = API()
res = api.get_bookings(date_from=datetime(2021,1,1), date_to=datetime(2021,12,31))

for booking in res:
    booking_id = booking['id']
    booking_details = api.get_booking_details(booking_id)
    a = 0