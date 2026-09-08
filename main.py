from manager import Manager, Authentication
from menus.menus import landing_page


def main():
    manager = Manager()
    manager.load_data()
    auth = Authentication(manager)

    landing_page(auth)


if __name__ == "__main__":
    main()
