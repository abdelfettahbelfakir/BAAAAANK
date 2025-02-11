class Menu:
    def __init__(self, title, options):
        self.title = title
        self.options = options

    def display(self):
        print(self.title)
        for i, option in enumerate(self.options, 1):
            print(f"{i}. {option}")

    def choose_option(self):
        choice = int(input("Tapez votre choix [1-9]: "))
        return choice
