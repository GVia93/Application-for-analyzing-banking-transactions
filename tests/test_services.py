import json

import pandas as pd
import pytest

from src.services import find_p2p_transfers


@pytest.fixture
def sample_data():
    """
    Пример тестового набора данных
    """
    df = [
        {"Категория": "Переводы", "Описание": "Иван И."},
        {"Категория": "Переводы", "Описание": "Петр П."},
        {"Категория": "Покупки", "Описание": "Магазин"},
        {"Категория": "Переводы", "Описание": "ООО Рога и Копыта"},
    ]
    return pd.DataFrame(df)


def test_find_p2p_transfers(sample_data):
    """Тест успешного поиска p2p транзакций."""
    result = find_p2p_transfers(sample_data)
    expected = json.dumps(
        [{"Категория": "Переводы", "Описание": "Иван И."}, {"Категория": "Переводы", "Описание": "Петр П."}],
        ensure_ascii=False,
        indent=2,
    )

    assert result == expected


def test_find_p2p_transfers_no_matches():
    """Тест, когда не проходят переводы."""
    df = pd.DataFrame(
        [
            {"Категория": "Покупки", "Описание": "Магазин"},
            {"Категория": "Переводы", "Описание": "ООО Рога и Копыта"},
        ]
    )
    result = find_p2p_transfers(df)
    assert result == json.dumps([], ensure_ascii=False, indent=2)


def test_find_p2p_transfers_invalid_data():
    """Тест, когда передаются некорректные данные."""
    result = find_p2p_transfers("невалидные данные")
    assert result is None
