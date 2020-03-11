# #!/usr/bin/env python

"""Tests for `lambda_function` package."""


import datetime
import unittest

from cd_dot_cz_price_search import lambda_function


class TestLambdaFunction(unittest.TestCase):
    """Tests for `lambda_function` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_get_dates(self):
        """Test something."""
        dates = lambda_function.get_dates(3, datetime.date(2020, 3, 11))
        self.assertEqual(dates, ["11.03.2020", "12.03.2020", "13.03.2020"])
