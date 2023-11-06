import csv
import datetime
import io

import numpy as np
import pandas as pd

from ..base import BaseData, DataValidationException


class GCDData(BaseData):
    def validate(self):
        super().validate()
        expected_columns = {
            "datetime": "datetime64[ms]",
            "time [sec]": "float64",
            "potential [V]": "float64",
            "capacity [mAh]": "float64",
            "capacity [mAh g-1]": "float64",
            "cycle": "int32",
            "step": "int32",
            "mode": "string",
        }

        for column, dtype in expected_columns.items():
            if column not in self.df.columns:
                raise DataValidationException(f"{column} is not in self.df.columns")
            if self.df[column].dtype != dtype:
                raise DataValidationException(
                    f"Invalid data type for {column}. Expected {dtype}, "
                    f"but found {self.df[column].dtype}."
                )


class SD8Data(GCDData):
    """
    Parse measurement data from Hokuto Denko SD8 system.
    """

    def load(self):
        headerRow: int
        started_at: datetime.datetime | None = None
        with open(self.file_path, mode="rt", encoding="shift_jis") as file:
            for i, line in enumerate(file.readlines()):
                if "測定開始日時" in line:
                    text = line.replace("測定開始日時,", "").replace("\n", "")
                    started_at = datetime.datetime.strptime(text, "%Y/%m/%d %H:%M:%S")
                if '"時間","電圧","電流","電力"' in line:
                    headerRow = i
                    break
                if i > 30:
                    raise DataValidationException("ヘッダー行が検出できませんでした")
        df = pd.read_csv(
            self.file_path,
            header=headerRow + 1,
            usecols=[0, 1, 4, 5, 10, 11, 12],
            names=["時間", "電圧", "Ah(Step)", "Ah/g(Step)", "サイクル", "ステップ", "モード"],
            dtype={
                "時間": "float64",
                "電圧": "float64",
                "Ah(Step)": "float64",
                "Ah/g(Step)": "float64",
                "サイクル": "int32",
                "ステップ": "int32",
                "モード": "string",
            },
            encoding="shift_jis",
            skip_blank_lines=True,
        )
        df.columns = [
            "time [sec]",
            "potential [V]",
            "capacity [mAh]",
            "capacity [mAh g-1]",
            "cycle",
            "step",
            "mode",
        ]
        if started_at is not None:
            df["datetime"] = started_at + pd.to_timedelta(df["time [sec]"], unit="s")
        else:
            df["datetime"] = None

        df = df.astype(
            dtype={
                "time [sec]": "float64",
                "datetime": "datetime64[ms]",
                "potential [V]": "float64",
                "capacity [mAh]": "float64",
                "capacity [mAh g-1]": "float64",
                "cycle": "int32",
                "step": "int32",
                "mode": "string",
            }
        )
        self.df = df


class BiologicData(GCDData):
    """
    Parse measurement data from Biologic system.
    """

    def load(self):
        df = pd.read_csv(self.file_path, sep="\t")
        df = df.rename(
            columns={
                "mode": "measure_mode",
                "time/s": "datetime",
                "Ewe/V": "potential [V]",
                "<I>/mA": "current [mA]",
                "Capacity/mA.h": "capacity [mAh]",
                "cycle number": "cycle",
            }
        )

        df.loc[(df["current [mA]"] == 0.0), "mode"] = "Rest"
        df.loc[(df["current [mA]"] < 0.0), "mode"] = "Discharge"
        df.loc[(df["current [mA]"] > 0.0), "mode"] = "Charge"

        df["datetime"] = pd.to_datetime(df["datetime"], format="%m/%d/%Y %H:%M:%S.%f")
        start = df["datetime"].iat[0]
        df["time [sec]"] = (df["datetime"] - start).dt.total_seconds()

        df = df.astype(
            dtype={
                "datetime": "datetime64[ms]",
                "potential [V]": "float64",
                "capacity [mAh]": "float64",
                "cycle": "int32",
                "mode": "string",
            }
        )

        for cycle, cycle_df in df.groupby("cycle"):
            df.loc[(df["cycle"] == cycle), "step"] = (
                cycle_df["mode"] != cycle_df["mode"].shift()
            ).cumsum()

        df.loc[df["step"].isna(), "step"] = 0

        df["cycle"] = df["cycle"] + 1
        df["step"] = df["step"] + 1

        df = df[
            [
                "time [sec]",
                "datetime",
                "potential [V]",
                "capacity [mAh]",
                "cycle",
                "step",
                "mode",
            ]
        ]
        df["capacity [mAh g-1]"] = None
        df = df.astype(
            dtype={
                "time [sec]": "float64",
                "datetime": "datetime64[ms]",
                "potential [V]": "float64",
                "capacity [mAh]": "float64",
                "capacity [mAh g-1]": "float64",
                "cycle": "int32",
                "step": "int32",
                "mode": "string",
            }
        )
        self.df = df


class HZ7000Data(GCDData):
    """
    Parse measurement data from Hokuto Denko HZ7000 system.
    This class is for a csv file converted with the dedicated software "HZ7000.exe" from .SDP file.
    """

    def load(self):
        # 最初の5行を読み込む
        with open(self.file_path, mode="rt", encoding="shift_jis") as file:
            blocks = file.read().split("《測定フェイズヘッダ》")
            include, exclude = blocks[-1].split("《解析データヘッダ》")  # 最後にくっついてる余分な分を取り除く
            blocks[-1] = include

        # 最初のブロックで「充放電測定」である事を確かめる
        block1 = blocks[0]
        if not "CDC 充放電測定" in block1.split("\n")[1]:
            raise DataValidationException("HZ7000の充放電ファイルとして読み込めません")

        # データは2ブロック目以降にある
        # CDC前のOCV測定 or CDC本測定
        df_list = []
        for cycle_num, block in enumerate(blocks[1:]):
            lines = csv.reader(io.StringIO(block))
            started_at: datetime.datetime
            for header, row in enumerate(lines):
                if "開始時間" in row:
                    started_at = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                if "《測定データ》" in row:
                    break

            if "自然電位測定" in block.split("\n")[1]:
                # 自然電位測定
                # header でheader行数を取得している
                df = pd.read_csv(
                    io.StringIO(block),
                    header=header - 3,
                    usecols=[1, 2],
                    names=["time [sec]", "potential [V]"],
                    dtype={
                        "time [sec]": float,
                        "potential [V]": float,
                    },
                    encoding="shift_jis",
                )
                df["datetime"] = started_at + pd.to_timedelta(
                    df["time [sec]"], unit="s"
                )
                df["capacity [mAh]"] = 0.0
                df["capacity [mAh g-1]"] = 0.0
                df["cycle"] = cycle_num + 1
                df["step"] = 1
                df["mode"] = "Rest"
                df_list.append(df)

            elif "本測定" in block.split("\n")[1]:
                # 充放電測定
                df = pd.read_csv(
                    io.StringIO(block),
                    header=header - 3,
                    usecols=[1, 2, 3, 5, 6, 7, 8],
                    names=[
                        "time [sec]",
                        "potential [V]",
                        "current [A]",
                        "+Q [C]",
                        "-Q [C]",
                        "Sigma Q [C]",
                        "mode",
                    ],
                    dtype={
                        "time [sec]": float,
                        "potential [V]": float,
                        "current [A]": float,
                        "+Q [C]": float,
                        "-Q [C]": float,
                        "Sigma Q [C]": float,
                        "mode": object,
                    },
                    encoding="shift_jis",
                )
                df["datetime"] = started_at + pd.to_timedelta(
                    df["time [sec]"], unit="s"
                )
                df["cycle"] = cycle_num + 1
                df["step"] = 0
                df["capacity [mAh g-1]"] = None
                df["mode"] = df["mode"].replace(
                    ["放電", "充電", "休止"], ["Discharge", "Charge", "Rest"]
                )

                # ステップ数を書き出す
                df["step"] = (df["mode"] != df["mode"].shift()).cumsum()

                # 充放電容量を書き出す
                # 放電は -Q [C] を利用する
                df.loc[df["mode"] == "Discharge", "capacity [mAh]"] = (
                    df["-Q [C]"].map(np.abs).divide(3.6)
                )
                df.loc[df["mode"] == "Charge", "capacity [mAh]"] = (
                    df["+Q [C]"].map(np.abs).divide(3.6)
                )
                df_list.append(
                    df[
                        [
                            "datetime",
                            "time [sec]",
                            "potential [V]",
                            "capacity [mAh]",
                            "capacity [mAh g-1]",
                            "cycle",
                            "step",
                            "mode",
                        ]
                    ]
                )

        self.df = pd.concat(df_list, ignore_index=True).astype(
            dtype={
                "time [sec]": "float64",
                "datetime": "datetime64[ms]",
                "potential [V]": "float64",
                "capacity [mAh]": "float64",
                "capacity [mAh g-1]": "float64",
                "cycle": "int32",
                "step": "int32",
                "mode": "string",
            }
        )


def get_GCDData(file_path: str) -> GCDData:
    def try_parse(gcddata: GCDData):
        try:
            result = gcddata(file_path)
            return result
        except DataValidationException as e:
            return None

    result = try_parse(SD8Data)
    if result is None:
        result = try_parse(BiologicData)
    if result is None:
        result = try_parse(HZ7000Data)
    if result is None:
        raise DataValidationException(
            "None of the parsing classes could handle it properly."
        )
    return result
