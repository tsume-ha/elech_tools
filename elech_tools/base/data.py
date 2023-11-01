import pandas as pd


class BaseData:
    def __init__(self, filePath) -> None:
        self.filePath: str = filePath
        self.df: pd.DataFrame = None

        self.load()
        self.validate()

    def load(self):
        pass

    def validate(self):
        pass


class DataValidationException(Exception):
    pass
