from datetime import datetime

from simplybookapi.core import Core


class API(Core):

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
                     event_id: int = None,
                     is_confirmed: int = None,
                     dataframe_flag: bool = False):
        """
        Retrieves a list of booking from SB API.

        Args:
            date_from: A date or datetime of booking start range date to filter.
            date_to: A date or datetime of booking end range date to filter.
            created_date_from: A date or datetime of booking created date start range to filter.
            created_date_to: A date or datetime of booking created date end range to filter.
            edited_date_from: A date or datetime of booking edited range date to filter.
            edited_date_to: A date or datetime of booking edited range date to filter.
            unit_group_id: Gets bookings assigned for certain service provider.
            event_id: Gets bookings only for certain service.
            is_confirmed: Integer 1 or 0 to indicate if booking has been confirmed.
            dataframe_flag: Flag to indicate if results should be returned in a dataframe. Otherwise a list or dict of
                           results will be returned.

        Returns:
            A list or dataframe containing bookings matching filter criteria.
        """
        params = {"order": "start_date"}

        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
            if date_from.hour != 0 or date_from.minute != 0:
                params['time_from'] = date_from.strftime('%H:%M:%S')

        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')
            if date_to.hour != 0 or date_to.minute != 0:
                params['time_to'] = date_to.strftime('%H:%M:%S')

        if created_date_from:
            params['created_date_from'] = created_date_from.strftime('%Y-%m-%d')
            if created_date_from.hour != 0 or created_date_from.minute != 0:
                params['created_time_from'] = created_date_from.strftime('%H:%M:%S')

        if created_date_to:
            params['created_date_to'] = created_date_to.strftime('%Y-%m-%d')
            if created_date_to.hour != 0 or created_date_to.minute != 0:
                params['created_time_to'] = created_date_to.strftime('%H:%M:%S')

        if edited_date_from:
            params['edited_date_from'] = edited_date_from.strftime('%Y-%m-%d')
            if edited_date_from.hour != 0 or edited_date_from.minute != 0:
                params['edited_time_from'] = edited_date_from.strftime('%H:%M:%S')

        if edited_date_to:
            params['edited_date_to'] = edited_date_to.strftime('%Y-%m-%d')
            if edited_date_to.hour != 0 or edited_date_to.minute != 0:
                params['edited_time_to'] = edited_date_to.strftime('%H:%M:%S')

        if unit_group_id:
            params['unit_group_id'] = unit_group_id

        if event_id:
            params['event_id'] = event_id

        if is_confirmed:
            params['is_confirmed'] = is_confirmed

        return self.get('getBookings', params, 'admin', dataframe_flag=dataframe_flag)

    def get_booking_details(self,
                            booking_id: int,
                            dataframe_flag: bool = False):
        """
        Gets details for a booking by ID number.

        Args:
            booking_id: The ID number of the booking as an int
            dataframe_flag: Flag to indicate if results should be returned in a dataframe. Otherwise a list or dict of
                           results will be returned.

        Returns:
            A dict or dataframe containing the details of the booking requested.
        """
        params = (booking_id)
        return self.get('getBookingDetails', params, 'admin', dataframe_flag=dataframe_flag)

