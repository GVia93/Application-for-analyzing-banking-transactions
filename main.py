from src.reports import spending_by_category
from src.services import find_p2p_transfers, investment_bank, generate_transactions, analyze_profitable_cashback_categories
from src.utils import file_reader
from src.views import home_page, event_page

def main():
    """
    Основная функция, запускающая интерфейс командной строки для анализа банковских транзакций.

    Функция предоставляет следующие возможности:
    1. Главная страница: выводит информацию о текущих транзакциях, включая приветствие, сводку по картам,
       топ-5 транзакций, курсы валют и цены акций.
    2. Поиск переводов физическим лицам: выполняет поиск переводов, соответствующих определенному шаблону,
       и выводит результат в формате JSON.
    3. Отчет по категории: формирует отчет о расходах по указанной категории за последние три месяца от выбранной даты.
    4. Анализ кешбэка: анализирует выгодные категории повышенного кешбэка за выбранный месяц и год.
    5. Инвесткопилка: рассчитывает сумму, которую можно отложить в "Инвесткопилку" за указанный месяц.
    6. События за период: выводит сводную информацию о событиях за указанный период.
    7. Выход: завершает работу программы.

    Ввод пользователя:
    - "1" - Вызов главной страницы.
    - "2" - Поиск переводов физическим лицам.
    - "3" - Генерация отчета по категории.
    - "4" - Анализ кешбэка.
    - "5" - Расчет инвесткопилки.
    - "6" - События за период.
    - "0" - Выход из программы.

    Обработка ошибок:
    - Если ввод пользователя некорректен, программа запрашивает ввод повторно.
    - В случае ошибок при обработке данных, выводится соответствующее сообщение.
    """
    file_path = "data/operations.xlsx"
    df = file_reader(file_path)

    while True:
        user_input = input(
            "Выберите действие:\n"
            "1 - Главная страница\n"
            "2 - Найти переводы физическим лицам\n"
            "3 - Сформировать отчет по категории\n"
            "4 - Анализ кешбэка\n"
            "5 - Расчет инвесткопилки\n"
            "6 - События за период\n"
            "0 - Выход\n"
            "Ваш выбор: "
        )
        if user_input == "1":
            home = home_page(df)
            print(home if home else "Не удалось сформировать главную страницу.")

        elif user_input == "2":
            transfers = find_p2p_transfers(df)
            print(transfers if transfers else "Переводы физ. лицам не найден.")

        elif user_input == "3":
            category = input("Введите категорию: ")
            date = input("Введите дату (ДД.ММ.ГГГГ) или оставьте пустым для текущей даты: ")
            report = spending_by_category(df, category, date)
            print(report.to_string(index=False) if not report.empty else "Нет данных для выбранной категории")

        elif user_input == "4":
            year = int(input("Введите год (например, 2024): "))
            month = int(input("Введите номер месяца (1-12): "))
            cashback = analyze_profitable_cashback_categories(df, year, month)
            print(cashback if cashback else "Нет данных для анализа кешбэка.")

        elif user_input == "5":
            month = input("Введите месяц в формате ГГГГ.ММ: ")
            limit = int(input("Введите шаг округления (10, 50, 100): "))
            transactions = generate_transactions(df)
            savings = investment_bank(month, transactions, limit)
            print(f"Сумма, которую можно отложить: {savings}")

        elif user_input == "6":
            date = input("Введите конечную дату периода (ДД.ММ.ГГГГ): ")
            period = input("Введите тип периода (W - неделя, M - месяц, Y - год, ALL - все время): ").upper()
            events = event_page(df, date, period)
            print(events if events else "Не удалось получить события за указанный период.")

        elif user_input == "0":
            print("Выход из программы")
            break

        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")


if __name__ == "__main__":
    main()
