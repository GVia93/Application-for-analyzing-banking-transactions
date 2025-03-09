import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/reports.log", mode="a")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def save_report(filename: Optional[str] = None):
    """
    Декоратор для сохранения результата функции в JSON-файл.
    """

    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> any:
            result = func(*args, **kwargs)
            report_filename = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                if isinstance(result, pd.DataFrame):
                    result_to_save = result.to_dict(orient="records")
                else:
                    result_to_save = result
                with open(report_filename, "w", encoding="utf-8") as file:
                    json.dump(result_to_save, file, ensure_ascii=False, indent=2, default=str)
                logger.info(f"Отчет успешно сохранен в файл: {report_filename}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")
            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(df: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает DataFrame с тратами по заданной категории за последние три месяца.

    :param df: DataFrame с транзакциями.
    :param category: Название категории транзакций.
    :param date: Опциональная дата в формате 'DD.MM.YYYY'. Если не указана, берется текущая дата.
    :return: DataFrame с тратами по категории за последние три месяца.
    """
    try:
        end_date = datetime.strptime(date, "%d.%m.%Y") if date else datetime.today()
        start_date = end_date - timedelta(days=90)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        df["Сумма операции"] = df["Сумма операции"].astype(str).str.replace(",", ".").astype(float)
        filtered_df = df[
            (df["Категория"] == category)
            & (df["Дата операции"] >= start_date)
            & (df["Дата операции"] <= end_date)
            & (df["Сумма операции"] < 0)
        ]

        return filtered_df.reset_index(drop=True)

    except Exception as e:
        logger.error(f"Ошибка при фильтрации трат по категории '{category}': {e}")
        return pd.DataFrame()
