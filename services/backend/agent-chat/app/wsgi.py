# flake8: noqa
import time
import gvars


if gvars.DEBUG:
    time.sleep(1)


from service import create_app


app = create_app()

if __name__ == "__main__":

    app.run(
        host=gvars.FLASK_HOST,
        debug=gvars.DEBUG,
        port=gvars.FLASK_PORT
    )
