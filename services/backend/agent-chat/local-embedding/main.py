# flake8: noqa
from dotenv import load_dotenv


load_dotenv()


from dummy import import_dummy  # noqa
from imt import import_imt  # noqs


def main() -> None:
    # import_dummy()
    import_imt()
    print("main")


if __name__ == "__main__":
    main()
