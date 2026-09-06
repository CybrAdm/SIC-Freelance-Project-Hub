from manager import FreelanceManager, Authentication
from menus import landing_page


def main():
    manager = FreelanceManager()
    manager.load_data()
    auth = Authentication(manager)

    landing_page(auth)


if __name__ == "__main__":
    main()
