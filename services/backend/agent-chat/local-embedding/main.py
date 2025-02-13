# flake8: noqa
from dotenv import load_dotenv


load_dotenv("./.env")


import etl.extract
import etl.transform_content
import etl.transform_final_embeddings
import etl.load_to_index

from etl import utils


def main() -> None:
    utils.step = "EXTRACT"
    etl.extract.run()

    utils.step = "TRANSFORM CONTENT"
    etl.transform_content.run()

    utils.step = "TRANSFORM FINAL EMBEDDINGS"
    # etl.transform_final_embeddings.run()

    utils.step = "LOAD EMBEDDINGS TO VECTOR-DB"
    # etl.load_to_index.run()
    

if __name__ == "__main__":
    main()
