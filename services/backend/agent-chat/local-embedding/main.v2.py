# flake8: noqa
from dotenv import load_dotenv


load_dotenv("./.env")


import etl.extract
import etl.transform_content


def main() -> None:
    # etl.extract.run()
    etl.transform_content.run()
    


if __name__ == "__main__":
    main()
