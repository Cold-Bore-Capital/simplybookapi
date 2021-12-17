from simplybookapi.functions.admin.get_bookings import GetBookings

g = GetBookings(test_mode=False)

res = g.get_bookings()

a = 0