import json
import logging
import os
from datetime import datetime, timedelta

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


def filter_data_by_range(df: pd.DataFrame, date_str: str, range_type: str) -> pd.DataFrame:
    """
    Фильтрует данные DataFrame по заданному диапазону.
    """
    date = datetime.strptime(date_str, "%d.%m.%Y")
    if range_type == "W":
        start = date - timedelta(days=date.weekday())
    elif range_type == "M":
        start = date.replace(day=1)
    elif range_type == "Y":
        start = date.replace(month=1, day=1)
    elif range_type == "ALL":
        start = df["Дата операции"].min()
    else:
        start = date.replace(day=1)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    return df[(df["Дата операции"] >= start) & (df["Дата операции"] <= date)]


def summarize(df: pd.DataFrame, categories: list) -> list:
    """
    Формирует сводку по категориям с суммами расходов или доходов.
    """
    summary = df.groupby("Категория")["Сумма операции"].sum().abs().sort_values(ascending=False)
    main = [
        {"category": category, "amount": round(amount, 2)}
        for category, amount in summary.items()
        if category in categories
    ]
    other = summary[~summary.index.isin(categories)].sum()
    if other > 0:
        main.append({"category": "Остальное", "amount": round(other, 2)})
    return main


def event_page(df: pd.DataFrame, date_str: str, range_type: str = "M") -> str:
    """
    Формирует и возвращает данные страницы событий в формате JSON.

    Функция выполняет следующие действия:
    1. Считывает данные операций из файла Excel.
    2. Формирует сводку по категориям с суммами расходов или доходов.
    3. Загружает пользовательские настройки и получает курсы валют и цены акций.
    4. Возвращает итоговый результат в формате JSON.
    """
    df = filter_data_by_range(df, date_str, range_type)

    expenses = df[df["Сумма операции"] < 0]
    income = df[df["Сумма операции"] > 0]

    expenses_main = summarize(expenses, expenses["Категория"].unique()[:6])
    transfers_cash = summarize(expenses, ["Переводы", "Наличные"])
    income_main = summarize(income, income["Категория"].unique())

    user_settings = load_user_settings("user_settings.json")
    currency_rates = get_currency_rates(user_settings.get("user_currencies"))
    stock_prices = get_stock_prices(user_settings.get("user_stocks"))

    report = {
        "expenses": {
            "total_amount": round(abs(expenses["Сумма операции"].sum()), 2),
            "main": expenses_main,
            "transfers_and_cash": transfers_cash,
        },
        "income": {
            "total_amount": round(income["Сумма операции"].sum(), 2),
            "main": income_main,
        },
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(report, ensure_ascii=False, indent=2)


def home_page(df: pd.DataFrame) -> str | None:
    """
    Формирует и возвращает данные домашней страницы в формате JSON.

    Функция выполняет следующие действия:
    1. Считывает данные операций из файла Excel.
    2. Определяет приветствие в зависимости от текущего времени суток.
    3. Генерирует сводку по картам и выводит топ-5 транзакций.
    4. Загружает пользовательские настройки и получает курсы валют и цены акций.
    5. Возвращает итоговый результат в формате JSON.
    """
    try:
        greeting = get_greeting()
        card_summary = get_card_summary(df)
        top_transactions = get_top_transactions(df)

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
    except Exception as e:
        logger.error(f"Ошибка формирования JSON: {e}")
        return None


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


def get_card_summary(df: pd.DataFrame) -> list | dict:
    """
    Создает сводку расходов по номерам карт.
    """
    try:
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


def get_top_transactions(df: pd.DataFrame) -> list | dict:
    """
    Функция возвращает топ 5 транзакций.
    """
    try:
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
