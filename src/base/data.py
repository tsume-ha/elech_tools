import pandas as pd


class BaseData:
    def __init__(self, file_path) -> None:
        self.file_path: str = file_path
        self.df: pd.DataFrame = None

        try:
            self.load()
        except Exception as e:
            raise DataValidationException(e)
        self.validate()

    def load(self):
        pass

    def validate(self):
        pass


class DataValidationException(Exception):
    pass
