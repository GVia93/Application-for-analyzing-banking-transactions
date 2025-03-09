import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import load_user_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/views.log", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

load_dotenv(".env")


def home_page(data) -> str:
    """
    Формирует и возвращает данные домашней страницы в формате JSON.

    Функция выполняет следующие действия:
    1. Считывает данные операций из файла Excel.
    2. Определяет приветствие в зависимости от текущего времени суток.
    3. Генерирует сводку по картам и выводит топ-5 транзакций.
    4. Загружает пользовательские настройки и получает курсы валют и цены акций.
    5. Возвращает итоговый результат в формате JSON.
    """
    greeting = get_greeting()
    card_summary = get_card_summary(data)
    top_transactions = get_top_transactions(data)

    user_settings = load_user_settings("user_settings.json")
    currency_rates = get_currency_rates(user_settings.get("user_currencies"))
    stock_prices = get_stock_prices(user_settings.get("user_stocks"))
    result = {
        "greeting": greeting,
        "cards": card_summary,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = datetime.today().hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_summary(data: list) -> list | dict:
    """
    Создает сводку расходов по номерам карт.
    """
    try:
        df = pd.DataFrame(data)
        df["Номер карты"] = df["Номер карты"].astype(str).str[-4:]
        df = df[df["Сумма операции"] < 0]
        summary = df.groupby("Номер карты")["Сумма операции"].sum().abs()
        return [
            {"last_digits": card, "total_spent": round(total, 2), "cashback": int(total // 100)}
            for card, total in summary.items()
        ]
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return {}


def get_top_transactions(data: list) -> list | dict:
    """
    Функция возвращает топ 5 транзакций.
    """
    try:
        df = pd.DataFrame(data)
        top_transactions = df.nlargest(5, "Сумма операции")
        return [
            {
                "date": row["Дата операции"],
                "amount": round(row["Сумма операции"], 2),
                "category": row["Категория"],
                "description": row["Описание"],
            }
            for _, row in top_transactions.iterrows()
        ]
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return {}


def get_currency_rates(currencies: list) -> list | dict:
    """
    Функция для получения курсов валют через API Layer.
    """
    api_key = os.getenv("API_KEY_LAYER")
    headers = {"apikey": api_key}
    base_currency = "RUB"
    url = f"https://api.apilayer.com/fixer/latest?base={base_currency}&symbols={','.join(currencies)}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return [
            {
                "currency": currency,
                "rate": round(round(1 / data["rates"][currency], 6) if data["rates"].get(currency) else None, 2),
            }
            for currency in currencies
        ]
    except Exception as e:
        logger.error(f"Ошибка получения курса валют: {e}")
        return {}


def get_stock_prices(stocks: list) -> list:
    """
    Получение цен на акции через API Marketstack.
    """
    api_key = os.getenv("API_KEY_MARKETSTACK")
    url = "http://api.marketstack.com/v1/eod"
    prices = []

    for stock in stocks:
        params = {"access_key": api_key, "symbols": stock, "limit": 1}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "data" in data and data["data"]:
                prices.append({"stock": stock, "price": round(data["data"][0].get("close", 0), 2)})
            else:
                logger.error(f"Нет данных о цене для акции {stock}. Ответ API: {data}")

        except Exception as e:
            logger.error(f"Ошибка получения цены акции {stock}: {e}")

    return prices
