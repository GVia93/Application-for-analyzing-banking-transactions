from src.services import find_p2p_transfers
from src.utils import file_reader
from src.views import home_page


data = file_reader("data/operations.xlsx")

def main():
    # user_input = input("Главная = 1"
    #                    "Переводы физ лицам = 2"
    #                    "Отчеты = 3")
    # if user_input == 1:
    # home = home_page()
    # print(home)

    p2p_transfers = find_p2p_transfers(data)
    print(p2p_transfers)


    return

if __name__ == "__main__":
    main()


