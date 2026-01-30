def start():
    print("Welcome to Alpha9!")
    choice = input("Update the data [y/n] : ")
    if choice.lower() == "y":
        from Alpha9.pipeline import main_pipeline
        main_pipeline.run()
    print("Thank you for using Alpha9!")