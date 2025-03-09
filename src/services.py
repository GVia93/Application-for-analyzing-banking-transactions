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


def find_p2p_transfers(data) -> str | None:
    """
    Функция находит переводы физическим лицам.
    Возвращает JSON со всеми такими транзакциями.
    """
    try:
        df = pd.DataFrame(data)
        pattern = re.compile(r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.$")
        p2p_transfers = df[(df["Категория"] == "Переводы") & df["Описание"].str.match(pattern)]
        result = p2p_transfers.to_dict(orient="records")
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при поиске P2P переводов: {e}")
        return None
