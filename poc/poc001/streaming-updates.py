from flask import Flask, Response, json
import time

app = Flask(__name__)


def run_flow():
    steps = [
        {"step": 1, "message": "Sending data to API1"},
        {"step": 2, "message": "Sending data to API2"},
        {"step": 3, "message": "Parsing responses"},
        {"step": 4, "message": "Generating response"},
        {"step": 5, "message": "Completed!"}
    ]

    for step in steps:
        yield json.dumps(step) + "\n"
        time.sleep(2)


@app.route('/run/flow', methods=['GET'])
def flow():
    return Response(run_flow(), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
