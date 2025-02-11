# flake8: noqa
from dotenv import load_dotenv



load_dotenv("./.env")


import etl.extract
import etl.transform_content
import etl.transform_content_cleanup
import etl.transform_final_embeddings

from etl import utils


def main() -> None:
    utils.step = "EXTRACT"
    # etl.extract.run()

    utils.step = "TRANSFORM CONTENT"
    # etl.transform_content.run()

    utils.step = "TRANSFORM CONTENT CLEANUP"
    # etl.transform_content_cleanup.run()

    utils.step = "TRANSFORM FINAL EMBEDDINGS"
    etl.transform_final_embeddings.run()
    


if __name__ == "__main__":
    main()
