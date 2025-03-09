import json
import logging

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/utils.log", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def file_reader(file_path: str = "") -> pd.DataFrame:
    """
    Функция считывает данные из EXCEL-файла и возвращает dataframe.
    """
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        return pd.DataFrame()


def load_user_settings(file_path: str = "") -> dict:
    """
    Загрузка пользовательских настроек из JSON
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки user_settings.json: {e}")
        return {}
