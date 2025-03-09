import json
from datetime import datetime

from utils import (file_reader, get_card_summary, get_currency_rates, get_greeting, get_stock_prices,
                   get_top_transactions, load_user_settings)


def home_page(date_time_str: str, data: list) -> str:
    dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    greeting = get_greeting(dt.hour)
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


data = file_reader("data/operations.xlsx")
date_time_str = "2025-03-09 10:30:00"
print(home_page(date_time_str, data))
