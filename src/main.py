def start():
    print("Welcome to Alpha9!")
    choice = input("Update the data [y/n] : ")
    if choice.lower() == "y":
        from src.pipeline import update_data
        update_data.update()
    print("Thank you for using Alpha9!")