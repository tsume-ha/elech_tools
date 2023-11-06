import datetime
import unittest

import pandas as pd

from elech_tools.utils.search import Search, SearchDateTime


class TestSearch(unittest.TestCase):
    def test_get_nearest_index_int(self):
        array = [1, 2, 3, 4, 5]
        self.assertEqual(Search(array).get_nearest_index(3), 2)

    def test_get_nearest_index_float(self):
        array = [1.1, 2.2, 3.3, 4.4, 5.5]
        self.assertEqual(Search(array).get_nearest_index(3), 2)
        self.assertEqual(Search(array).get_nearest_index(3.2), 2)
        self.assertEqual(Search(array).get_nearest_index(3.9), 3)

    def test_get_nearest_index_pd_series(self):
        array = pd.Series([1.1, 2.2, 3.3, 4.4, 5.5])
        self.assertEqual(Search(array).get_nearest_index(3), 2)
        self.assertEqual(Search(array).get_nearest_index(3.9), 3)

    def test_get_nearest_index_pd_series_with_index(self):
        array = pd.Series([1.1, 2.2, 3.3, 4.4, 5.5], index=[11, 12, 13, 14, 15])
        self.assertEqual(Search(array).get_nearest_index(3), 13)
        self.assertEqual(Search(array).get_nearest_index(3.2), 13)
        self.assertEqual(Search(array).get_nearest_index(3.9), 14)

    def test_get_nearest_index_pd_dataframe(self):
        array = pd.DataFrame([1.1, 2.2, 3.3, 4.4, 5.5])
        self.assertEqual(Search(array).get_nearest_index(3), 2)
        self.assertEqual(Search(array).get_nearest_index(3.2), 2)
        self.assertEqual(Search(array).get_nearest_index(3.9), 3)

    def test_get_nearest_index_pd_dataframe_with_index(self):
        array = pd.DataFrame([1.1, 2.2, 3.3, 4.4, 5.5], index=[11, 12, 13, 14, 15])
        self.assertEqual(Search(array).get_nearest_index(3), 13)
        self.assertEqual(Search(array).get_nearest_index(3.4), 13)
        self.assertEqual(Search(array).get_nearest_index(3.9), 14)
        self.assertEqual(Search(array).get_nearest_index(5.4), 15)
        self.assertEqual(Search(array).get_nearest_index(5.6), 15)

    def test_get_nearest_index_int_sort(self):
        array = [3, 2, 4, 6, 1]
        self.assertEqual(Search(array).sort().get_nearest_index(3), 0)
        self.assertEqual(Search(array).sort().get_nearest_index(2), 1)
        self.assertEqual(Search(array).sort().get_nearest_index(4), 2)

    def test_get_nearest_index_float(self):
        array = [3.3, 2.2, 4.1, 6.6, 1.0]
        self.assertEqual(Search(array).sort().get_nearest_index(3), 0)
        self.assertEqual(Search(array).sort().get_nearest_index(3.9), 2)
        self.assertEqual(Search(array).sort().get_nearest_index(6.7), 3)


class TestSearchDateTime(unittest.TestCase):
    def test_get_nearest_time(self):
        now = datetime.datetime.now()
        array = [now + datetime.timedelta(minutes=i * 10) for i in range(5)]
        time = now + datetime.timedelta(minutes=22)
        self.assertEqual(SearchDateTime(array).get_nearest_index(time), 2)

    def test_get_nearest_time_sort(self):
        now = datetime.datetime.now()
        array = [
            now + datetime.timedelta(minutes=30),  # 0
            now + datetime.timedelta(minutes=10),  # 1
            now + datetime.timedelta(minutes=20),  # 2
            now + datetime.timedelta(minutes=50),  # 3
        ]
        self.assertEqual(
            SearchDateTime(array)
            .sort()
            .get_nearest_index(now + datetime.timedelta(minutes=21)),
            2,
        )
        self.assertEqual(
            SearchDateTime(array)
            .sort()
            .get_nearest_index(now + datetime.timedelta(minutes=33)),
            0,
        )
        self.assertEqual(
            SearchDateTime(array)
            .sort()
            .get_nearest_index(now + datetime.timedelta(minutes=44)),
            3,
        )

    def test_get_nearest_time_str(self):
        array = [
            "2023-09-08 10:00:00",
            "2023-09-08 11:00:00",
            "2023-09-08 12:00:00",
            "2023-09-08 13:00:00",
            "2023-09-08 14:00:00",
        ]
        self.assertEqual(
            SearchDateTime(array).get_nearest_index("2023-09-08 12:10:00"), 2
        )

    def test_get_nearest_time_str_sort(self):
        array = [
            "2023-09-08 10:00:00",
            "2023-09-08 13:00:00",
            "2023-09-08 11:00:00",
            "2023-09-08 14:00:00",
            "2023-09-08 12:00:00",
        ]
        self.assertEqual(
            SearchDateTime(array).sort().get_nearest_index("2023-09-08 12:10:01"), 4
        )

    def test_get_nearest_time_series(self):
        array = pd.Series(
            [
                "2023-09-08 10:00:00",
                "2023-09-08 11:00:00",
                "2023-09-08 12:00:00",
                "2023-09-08 13:00:00",
                "2023-09-08 14:00:00",
            ]
        )
        self.assertEqual(
            SearchDateTime(array).get_nearest_index(
                datetime.datetime.strptime("2023-09-08 12:10:01", "%Y-%m-%d %H:%M:%S")
            ),
            2,
        )

    def test_get_nearest_time_series_index(self):
        array = pd.Series(
            [1, 2, 3, 4, 5],
            index=[
                "2023-09-08 10:00:00",
                "2023-09-08 11:00:00",
                "2023-09-08 12:00:00",
                "2023-09-08 13:00:00",
                "2023-09-08 14:00:00",
            ],
        )
        self.assertEqual(
            SearchDateTime(array.index).get_nearest_index(
                datetime.datetime.strptime("2023-09-08 13:10:01", "%Y-%m-%d %H:%M:%S")
            ),
            3,
        )
        # indexがDatetimeIndexでも動作する
        array.index = array.index.map(lambda t: pd.Timestamp(t))
        self.assertEqual(
            SearchDateTime(array.index).get_nearest_index("2023-09-08 13:10:01"), 3
        )
