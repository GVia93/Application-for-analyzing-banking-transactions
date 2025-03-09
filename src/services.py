import json
import re

import pandas as pd

from src.utils import file_reader


def find_p2p_transfers(data) -> str:
    """
    Функция находит переводы физическим лицам.
    Возвращает JSON со всеми такими транзакциями.
    """
    df = pd.DataFrame(data)
    pattern = re.compile(r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.$")
    p2p_transfers = df[(df["Категория"] == "Переводы") & df["Описание"].str.match(pattern)]

    result = p2p_transfers.to_dict(orient="records")
    return json.dumps(result, ensure_ascii=False, indent=2)
