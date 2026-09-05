def start():
    print("Welcome to Alpha9!")
    choice = input("Update the data [y/n] : ")
    if choice.lower() == "y":
        from pipeline import main_pipeline
        choice = input('Download the data [y/n] : ')
        main_pipeline.run(choice)
    choice = input('Backtest [y/n] : ')
    if choice.lower() == "y":
        from backtest import main_backtest
        # data_type = input('Enter the type of data : ')
        data_type = 'train'
        # _start = input('Enter the start date : ')
        _start = '2021-01-01'
        # end = input('Enter the end date : ')
        end = '2023-12-31 23:59:59'
        main_backtest.run(data_type, _start, end)
    print("Thank you for using Alpha9!")
