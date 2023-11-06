import numpy as np
import pandas as pd


class Search:
    def __init__(self, arrayLike):
        self.series: pd.Series = self.to_series(arrayLike)

    def to_series(self, arrayLike) -> pd.Series:
        if isinstance(arrayLike, np.ndarray):
            return pd.Series(arrayLike)
        elif isinstance(arrayLike, pd.Series):
            return arrayLike
        elif isinstance(arrayLike, pd.DataFrame):
            if len(arrayLike.columns) > 1:
                raise Exception("columnが2つ以上あるDataFrameでは探索できません")
            return arrayLike.iloc[:, 0]
        else:
            return pd.Series(arrayLike)

    def sort(self):
        self.series = self.series.sort_values(kind="mergesort", ignore_index=False)
        return self

    def get_nearest_index(self, value) -> pd.Index | pd.MultiIndex:
        array = self.series.values
        index = array.searchsorted(value, side="left")

        if index == 0:
            # 探した場所が最初
            pass
        elif index == len(array):
            # 探した場所が最後
            index = index - 1
        else:
            # iは, a[i−1]<v≤a[i] を満たす
            # 隣が最小かもしれない
            if np.abs(array[index - 1] - value) < np.abs(array[index] - value):
                index = index - 1

        return self.series.index[index]


class SearchDateTime(Search):
    """
    datetimeを対象にした検索
    """

    def to_series(self, arrayLike) -> pd.Series:
        series = super().to_series(arrayLike)
        series = pd.to_datetime(series)
        series = series.apply(lambda t: t.timestamp())
        return series

    def get_nearest_index(self, value):
        timestamp: pd.Timestamp = pd.to_datetime(value)
        unixtime = timestamp.timestamp()
        return super().get_nearest_index(unixtime)
