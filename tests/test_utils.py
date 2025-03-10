from unittest.mock import mock_open, patch

from src.utils import load_user_settings


@patch("builtins.open", new_callable=mock_open, read_data='[{"id": 1, "amount": 100}]')
def test_load_user_settings_success(mock_file):
    """
    Тестирует успешную загрузку данных из JSON-файла.
    Ожидается, что функция вернет список транзакций, если файл существует и содержит валидный JSON-список.
    """
    result = load_user_settings("dummy_path.json")
    assert result == [{"id": 1, "amount": 100}]


@patch("builtins.open", side_effect=FileNotFoundError)
def test_load_user_settings_file_not_found(mock_file):
    """
    Тестирует обработку случая, когда файл не существует.
    Ожидается, что функция вернет пустой список, если файл не найден.
    """
    result = load_user_settings("nonexistent_file.json")
    assert result == []


@patch("builtins.open", new_callable=mock_open, read_data="invalid json")
def test_load_user_settings_invalid_json(mock_file):
    """
    Тестирует обработку случая, когда JSON в файле некорректен.
    Ожидается, что функция вернет пустой список, если JSON не может быть декодирован.
    """
    result = load_user_settings("invalid.json")
    assert result == []
