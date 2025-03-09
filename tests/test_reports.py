import json
import pytest
import pandas as pd
from src.reports import spending_by_category, save_report

@pytest.fixture
def sample_dataframe():
    """Пример тестового DataFrame."""
    data = {
        "Дата операции": ["31.12.2021 16:44:00", "30.12.2021 16:44:00", "01.01.2022 10:00:00"],
        "Категория": ["Супермаркеты", "Супермаркеты", "Развлечения"],
        "Сумма операции": ["-100,00", "-200,00", "-50,00"]
    }
    return pd.DataFrame(data)

def test_spending_by_category(sample_dataframe):
    """Тестирование фильтрации по категории и дате."""
    result = spending_by_category(sample_dataframe, "Супермаркеты", "31.12.2021")
    assert not result.empty
    assert len(result) == 2
    assert all(result["Категория"] == "Супермаркеты")
    assert all(result["Сумма операции"] < 0)

def test_spending_by_category_no_results(sample_dataframe):
    """Тестирование, когда нет совпадений."""
    result = spending_by_category(sample_dataframe, "Транспорт", "31.12.2021")
    assert result.empty

def test_save_report_decorator(tmp_path):
    """Тестирование сохранения отчета через декоратор."""
    test_file = tmp_path / "test_report.json"

    @save_report(filename=str(test_file))
    def generate_report():
        return {"status": "success", "data": [1, 2, 3]}

    result = generate_report()

    # Проверяем, что файл создан
    assert test_file.exists()

    # Проверяем содержимое файла
    with open(test_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        assert data == result
