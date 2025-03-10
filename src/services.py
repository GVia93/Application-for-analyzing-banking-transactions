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
