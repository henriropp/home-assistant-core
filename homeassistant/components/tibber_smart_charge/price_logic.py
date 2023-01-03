"""Price logic."""

import logging

from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


class PriceLogic:
    """Price logic for smart charging."""

    def __init__(self, price_dict):
        """Init."""
        self._price_list = list(price_dict.items())
        self._price_list.sort(key=lambda a: a[1])
        self._hours = []

    def find_cheapest_hours(self, count, time_from=None):
        """Find cheapest number of hours starting from time_from."""
        filtered_list = self._price_list
        if time_from:
            filtered_list = list(
                filter(
                    lambda ti: dt_util.parse_datetime(ti[0]) >= time_from, filtered_list
                )
            )
        result = filtered_list[0:count]
        result.sort(key=lambda a: a[0])
        return result

    def calculate_cheapest_hours(self, time_from):
        """Calculate checpest hours 1-10."""
        self._hours.clear()
        for i in range(1, 11):
            hours = self.find_cheapest_hours(i, time_from)
            self._hours.append(hours)
            _LOGGER.info("Hours %d: %s", i, hours)

    def get_cheapest_hours(self, count):
        """Get calculated hours."""
        return self._hours[count - 1]
