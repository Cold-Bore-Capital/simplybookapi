from datetime import datetime
import json
from simplybookapi.main import Main


class GetBookings(Main):
    """
    getBookings RPC function.
    """

    def __init__(self, test_mode=False):
        super().__init__(test_mode)

    def get_bookings(self,
                     date_from: datetime = None,
                     date_to: datetime = None,
                     created_date_from: datetime = None,
                     created_date_to: datetime = None,
                     edited_date_from: datetime = None,
                     edited_date_to: datetime = None,
                     unit_group_id: int = None,
                     is_confirmed: int = None,
                     dataframe_flag: bool = False):
        params = {'order': 'start_date'}

        if date_from:
            params['date_from'] = date_from

        if date_to:
            params['date_to'] = date_to

        if created_date_from:
            params['created_date_from'] = created_date_from

        if created_date_to:
            params['created_date_to'] = created_date_to

        if edited_date_from:
            params['edited_date_from'] = edited_date_from

        if edited_date_to:
            params['edited_date_to'] = edited_date_to

        if unit_group_id:
            params['unit_group_id'] = unit_group_id

        if is_confirmed:
            params['is_confirmed'] = is_confirmed

        return self.get('getBookings', params, 'admin', dataframe_flag=dataframe_flag)
