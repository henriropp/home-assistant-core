"""Test of price logic."""
import unittest

import price_logic

from homeassistant.util import dt as dt_util

prices = {
    "2023-01-02T00:00:00.000+01:00": 0.9143,
    "2023-01-02T01:00:00.000+01:00": 0.8275,
    "2023-01-02T02:00:00.000+01:00": 0.8441,
    "2023-01-02T03:00:00.000+01:00": 0.7232,
    "2023-01-02T04:00:00.000+01:00": 0.8054,
    "2023-01-02T05:00:00.000+01:00": 1.0925,
    "2023-01-02T06:00:00.000+01:00": 1.5349,
    "2023-01-02T07:00:00.000+01:00": 2.0301,
    "2023-01-02T08:00:00.000+01:00": 2.1384,
    "2023-01-02T09:00:00.000+01:00": 2.1532,
    "2023-01-02T10:00:00.000+01:00": 2.1332,
    "2023-01-02T11:00:00.000+01:00": 2.1018,
    "2023-01-02T12:00:00.000+01:00": 2.1161,
    "2023-01-02T13:00:00.000+01:00": 2.1075,
    "2023-01-02T14:00:00.000+01:00": 2.1692,
    "2023-01-02T15:00:00.000+01:00": 2.2685,
    "2023-01-02T16:00:00.000+01:00": 2.3734,
    "2023-01-02T17:00:00.000+01:00": 2.4722,
    "2023-01-02T18:00:00.000+01:00": 2.5381,
    "2023-01-02T19:00:00.000+01:00": 2.3952,
    "2023-01-02T20:00:00.000+01:00": 2.2359,
    "2023-01-02T21:00:00.000+01:00": 2.0785,
    "2023-01-02T22:00:00.000+01:00": 1.9395,
    "2023-01-02T23:00:00.000+01:00": 1.7503,
}


class MyTestCase(unittest.TestCase):
    """Test of price logic."""

    def test_find_cheapest_hour(self):
        """Test of price logic."""
        pl = price_logic.PriceLogic(prices)

        cheapest = pl.find_cheapest_hours(1)
        self.assertEqual(
            "2023-01-02T03:00:00.000+01:00", cheapest[0][0]
        )  # add assertion here
        self.assertEqual(0.7232, cheapest[0][1])  # add assertion here

        cheapest = pl.find_cheapest_hours(2)
        self.assertEqual(
            "2023-01-02T03:00:00.000+01:00", cheapest[0][0]
        )  # add assertion here
        self.assertEqual(0.7232, cheapest[0][1])  # add assertion here
        self.assertEqual(
            "2023-01-02T04:00:00.000+01:00", cheapest[1][0]
        )  # add assertion here
        self.assertEqual(0.8054, cheapest[1][1])  # add assertion here

        cheapest = pl.find_cheapest_hours(3)
        self.assertEqual(
            "2023-01-02T01:00:00.000+01:00", cheapest[0][0]
        )  # add assertion here
        self.assertEqual(0.8275, cheapest[0][1])  # add assertion here
        self.assertEqual(
            "2023-01-02T03:00:00.000+01:00", cheapest[1][0]
        )  # add assertion here
        self.assertEqual(0.7232, cheapest[1][1])  # add assertion here
        self.assertEqual(
            "2023-01-02T04:00:00.000+01:00", cheapest[2][0]
        )  # add assertion here
        self.assertEqual(0.8054, cheapest[2][1])  # add assertion here

    def test_find_cheapest_hour_with_start_time(self):
        """Test of price logic."""
        pl = price_logic.PriceLogic(prices)

        cheapest = pl.find_cheapest_hours(
            1, dt_util.parse_datetime("2023-01-02T04:00:00.000+01:00")
        )
        self.assertEqual(
            "2023-01-02T04:00:00.000+01:00", cheapest[0][0]
        )  # add assertion here
        self.assertEqual(0.8054, cheapest[0][1])  # add assertion here

        cheapest = pl.find_cheapest_hours(
            2, dt_util.parse_datetime("2023-01-02T04:00:00.000+01:00")
        )
        self.assertEqual(
            "2023-01-02T04:00:00.000+01:00", cheapest[0][0]
        )  # add assertion here
        self.assertEqual(0.8054, cheapest[0][1])  # add assertion here
        self.assertEqual(
            "2023-01-02T05:00:00.000+01:00", cheapest[1][0]
        )  # add assertion here
        self.assertEqual(1.0925, cheapest[1][1])  # add assertion here

        cheapest = pl.find_cheapest_hours(
            3, dt_util.parse_datetime("2023-01-02T04:00:00.000+01:00")
        )
        self.assertEqual(
            "2023-01-02T04:00:00.000+01:00", cheapest[0][0]
        )  # add assertion here
        self.assertEqual(0.8054, cheapest[0][1])  # add assertion here
        self.assertEqual(
            "2023-01-02T05:00:00.000+01:00", cheapest[1][0]
        )  # add assertion here
        self.assertEqual(1.0925, cheapest[1][1])  # add assertion here
        self.assertEqual(
            "2023-01-02T06:00:00.000+01:00", cheapest[2][0]
        )  # add assertion here
        self.assertEqual(1.5349, cheapest[2][1])  # add assertion here


if __name__ == "__main__":
    unittest.main()
