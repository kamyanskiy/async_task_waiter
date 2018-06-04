import flask
import random
import time

app = flask.Flask(__name__)

@app.route("/url/<int:api_id>")
def handler(api_id):
    # sleep = random.randint(0, 5)
    print(f"Sleep {api_id} seconds")
    time.sleep(api_id)
    return flask.jsonify({"result":f"slept {api_id} seconds",
                          "api_id": api_id})

if __name__ == "__main__":
    app.run(debug=True, port=8001)