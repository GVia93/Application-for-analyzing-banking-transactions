import json
import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/services.log", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def find_p2p_transfers(df: pd.DataFrame) -> str | None:
    """
    Функция находит переводы физическим лицам.
    Возвращает JSON со всеми такими транзакциями.
    """
    try:
        if not isinstance(df, pd.DataFrame):
            logger.error(f"Не корректный формат данных.")
            raise ValueError()

        pattern = re.compile(r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.$")
        p2p_transfers = df[(df["Категория"] == "Переводы") & df["Описание"].str.match(pattern, na=False)]

        if not p2p_transfers.empty:
            result = p2p_transfers.to_dict(orient="records")
            return json.dumps(result, ensure_ascii=False, indent=2)

        logger.info("Нет подходящих P2P переводов.")
        return json.dumps([], ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка при поиске P2P переводов: {e}")
        return None


def generate_transactions(df: pd.DataFrame) -> list:
    """
    Функция формирует список транзакций из DataFrame.
    """
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    df["Дата операции"] = df["Дата операции"].dt.strftime("%Y.%m.%d")
    filtered_df = df[["Дата операции", "Сумма операции"]]
    transactions = filtered_df.to_dict(orient="records")
    return transactions


def investment_bank(month: str, transactions: list[dict[str, any]], limit: int) -> float:
    """
    Рассчитывает сумму, которую можно отложить в "Инвесткопилку" за указанный месяц.

    :param month: Месяц в формате 'YYYY.MM'.
    :param transactions: Список транзакций с полями 'Дата операции' и 'Сумма операции'.
    :param limit: Шаг округления (10, 50 или 100).
    :return: Общая сумма, которая будет отложена в "Инвесткопилку".
    """
    try:
        total_savings = 0.0

        for transaction in transactions:
            date = transaction.get("Дата операции")
            amount = transaction.get("Сумма операции")

            if date and amount and date.startswith(month) and amount < 0:
                rounded = ((abs(amount) // limit) + 1) * limit
                savings = rounded - abs(amount)
                total_savings += savings

        return round(total_savings, 2)
    except Exception as e:
        logging.error(f"Ошибка при расчете инвесткопилки: {e}")
        return 0.0


def analyze_profitable_cashback_categories(df: pd.DataFrame, year: int, month: int) -> str | list:
    """
    Анализирует выгодные категории повышенного кешбэка за указанный месяц и год.
    """
    try:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        filtered = df[(df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)]
        filtered = filtered[filtered["Сумма операции"] < 0]
        cashback_rate = 0.05
        cashback_summary = (
            filtered.groupby("Категория")["Сумма операции"]
            .sum()
            .abs()
            .apply(lambda x: round(x * cashback_rate, 2))
            .to_dict()
        )

        return json.dumps(cashback_summary, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка при анализе кешбэка: {e}")
        return []
