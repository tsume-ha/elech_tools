from typing import Literal

from matplotlib.axes import Axes

from .data import GCDData

Mode = Literal["Charge", "Discharge"]
ModeAll = Literal["Rest", "Charge", "Discharge"]


class GCDAnalyser:
    def __init__(self, data: GCDData) -> None:
        self.data: GCDData = data
        self.steps: list[list[tuple(tuple(int, int), ModeAll)]] = []
        self._discharges: list[tuple(int, int)] = []
        self._charges: list[tuple(int, int)] = []
        for cycle_index, cycle in self.data.df.groupby("cycle"):
            mode_in_steps: list[Mode] = []
            for step_index, step in cycle.groupby("step"):
                mode = step["mode"].iat[0]
                mode_in_steps.append(((cycle_index, step_index), mode))
                if mode == "Discharge":
                    self._discharges.append((cycle_index, step_index))
                elif mode == "Charge":
                    self._charges.append((cycle_index, step_index))
                else:
                    pass
            self.steps.append(mode_in_steps)

    def get_index(self, cycle: int, mode: Literal["Charge", "Discharge"]):
        """
        全サイクルの中から、指定の測定結果のcycle, modeをタプルで返します

        ----------
        Parameters
        cycle: int
            サイクル数。Restのみのサイクルは無視します。1始まり
            1 => 1st サイクル
            10 => 10th サイクル
        mode: Literal["Charge", "Discharge"]
            動作モード。Restは指定できません。

        Returns
        tuple(int, int)
        """
        if mode == "Charge":
            return self._charges[cycle - 1]
        elif mode == "Discharge":
            return self._discharges[cycle - 1]
        else:
            raise Exception("Rest Mode can not be specified.")

    def get_df(self, cycle: int, mode: Literal["Charge", "Discharge"]):
        """
        全サイクルの中から、指定の測定結果のDataFrameを返します

        ----------
        Parameters
        cycle: int
            サイクル数。Restのみのサイクルは無視します。1始まり
            1 => 1st サイクル
            10 => 10th サイクル
        mode: Literal["Charge", "Discharge"]
            動作モード。Restは指定できません。

        Return
        pandas.DataFrame
        """
        index = self.get_index(cycle, mode)
        return self.data.df.groupby(["cycle", "step"]).get_group(index)

    def plot_charge_discharge(
        self, ax: Axes, cycle: int, mode: Literal["Charge", "Discharge"], **kwargs
    ):
        """
        指定されたサイクルの充放電曲線をプロットします

        ----------
        Parameters
        ax: matplotlib.axes.Axes
        cycle: int
            サイクル数。Restのみのサイクルは無視します。1始まり
            1 => 1st サイクル
            10 => 10th サイクル
        mode: Literal["Charge", "Discharge"]
            充放電モード。Restは無視するため、指定できません。
        **kwargs: プロットの設定です. axes.plotへ代入されます.
            color, labelなどが設定可です. 詳しくは
            https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html

        Return
        matplotlib.axes.Axes
        """
        df = self.get_df(cycle=cycle, mode=mode)
        x = df["capacity [mAh g-1]"]
        y = df["potential [V]"]

        ax.plot(x, y, **kwargs)
        ax.set_xlabel(r"Capacity / $\mathrm{mAh\,g^{-1}}$")
        ax.set_ylabel("Potential / V")
        return ax

    def plot_potential_by_time(
        self,
        ax: Axes,
        index_start: int | None = None,
        index_end: int | None = None,
        time_unit: Literal["s", "m", "h"] = "s",
        **kwargs,
    ):
        """
        指定された範囲の時間-電位をプロットします.

        ----------
        Parameters
        ax: matplotlib.axes.Axes
        index_start: int | None
        index_end: int | None
            描画するDataFrameの範囲です。`df.loc[index_start:index_end]`
            メソッドで利用します.
            Noneのときは全範囲になります.
        time_unit: Literal["s", "m", "h"] = "s"
            横軸の時間の単位です. 秒(s), 分(m), 時(h)のいずれかが指定できます.
            デフォルトは秒(s)です.
        **kwargs: プロットの設定です. axes.plotへ代入されます.
            color, labelなどが設定可です. 詳しくは
            https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html

        Return
        matplotlib.axes.Axes
        """

        df = self.data.df
        if index_start is None:
            index_start = df.index[0]
        if index_end is None:
            index_end = df.index[-1]
        df = df.loc[index_start:index_end]
        if time_unit == "s":
            x = df["time [sec]"]
        elif time_unit == "m":
            x = df["time [sec]"] / 60
        elif time_unit == "h":
            x = df["time [sec]"] / 3600
        else:
            raise Exception("Specify time_unit as one of s, m or h.")
        y = df["potential [V]"]

        ax.plot(x, y, **kwargs)
        ax.set_xlabel(f"Time / {time_unit}")
        ax.set_ylabel("Potential / V")

        return ax
