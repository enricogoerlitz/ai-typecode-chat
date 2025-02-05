# flake8: noqa
import time

from dotenv import load_dotenv


load_dotenv()


import gvars


if gvars.DEBUG == "true":
    print("DEBUG WAIT")
    time.sleep(2)


from service import create_app


app = create_app()

if __name__ == "__main__":

    app.run(
        host=gvars.FLASK_HOST,
        debug=gvars.DEBUG,
        port=gvars.FLASK_PORT
    )
