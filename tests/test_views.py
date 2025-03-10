from unittest.mock import patch

import pandas as pd
import pytest

from src.views import get_card_summary, get_greeting, get_top_transactions, home_page


@pytest.fixture
def sample_df():
    """Создает тестовый DataFrame с примерами транзакций."""
    return pd.DataFrame(
        {
            "Дата операции": ["01.01.2024 12:00:00", "02.01.2024 13:00:00"],
            "Категория": ["Покупки", "Переводы"],
            "Сумма операции": [-100.0, -200.0],
            "Описание": ["Магазин", "Иван И."],
            "Номер карты": ["1234567890123456", "9876543210987654"],
        }
    )


def test_get_greeting():
    """Проверяет, что функция возвращает корректное приветствие."""
    greeting = get_greeting()
    assert greeting in ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]


def test_get_card_summary(sample_df):
    """Тестирует корректность сводки по картам."""
    summary = get_card_summary(sample_df)
    assert isinstance(summary, list)
    assert len(summary) == 2


def test_get_top_transactions(sample_df):
    """Проверяет, что функция возвращает топ-5 транзакций."""
    top_transactions = get_top_transactions(sample_df)
    assert isinstance(top_transactions, list)
    assert len(top_transactions) <= 5


def test_home_page(sample_df):
    """Тестирует корректность формирования домашней страницы."""
    with patch("src.views.load_user_settings", return_value={"user_currencies": [], "user_stocks": []}):
        result = home_page(sample_df)
        assert result is not None
        assert isinstance(result, str)
