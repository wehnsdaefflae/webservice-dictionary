import json
import time
from pathlib import Path
from typing import Optional, Dict

import flask
from flask import jsonify, Response, request


class Server:
    app = flask.Flask(__name__)
    # app.config["DEBUG"] = True  # automatic reload on code change

    path_file = Path("dictionary.json")
    if path_file.is_file():
        with path_file.open(mode="r") as file:
            dictionary = json.load(file)
    else:
        dictionary = dict()

    time_write_last = time.time()

    @staticmethod
    def _backup():
        time_now = time.time()
        if 10. < time_now - Server.time_write_last:
            with Server.path_file.open(mode="w") as file:
                json.dump(Server.dictionary, file, indent=2, sort_keys=True)
            Server.time_write_last = time_now

    @staticmethod
    def pop(key: str) -> Optional[str]:
        try:
            value = Server.dictionary.pop(key)
        except KeyError as e:
            raise e
        finally:
            Server._backup()
        return value

    @staticmethod
    def get(key: str) -> Optional[str]:
        return Server.dictionary.get(key)

    @staticmethod
    def complete() -> Dict[str, str]:
        return Server.dictionary

    @staticmethod
    def set(key: str, value: str):
        Server.dictionary[key] = value
        Server._backup()


@Server.app.route("/", methods=["GET"])
def home() -> Response:
    return jsonify(msg="<h1>Webservice Dictionary</h1><p>This site is a prototype API for a Python dictionary.</p>")


@Server.app.route("/api/webservice-dictionary/v1/set/", methods=["PUT"])
def set_value() -> Response:
    key = request.form.get("key")
    if key is None:
        return jsonify(msg="no key parameter received")

    value = request.form.get("value")
    if value is None:
        return jsonify(msg="no value parameter received")

    Server.set(key, value)
    return jsonify(msg="key mapped to value")


@Server.app.route("/api/webservice-dictionary/v1/pop/", methods=["PUT"])
def pop_value() -> Response:
    key = request.form.get("key")
    if key is None:
        return jsonify(msg="no key parameter received")

    try:
        value = Server.pop(key)

    except KeyError as e:
        return jsonify(msg=str(e))

    return jsonify(value=value)


@Server.app.route("/api/webservice-dictionary/v1/get/", methods=["GET"])
def get_value() -> Response:
    key = request.args.get("key")
    if key is None:
        return jsonify(msg="no key parameter received")

    value = Server.get(key)
    if value is None:
        return jsonify(msg=f"no value for key '{key:s}'")

    return jsonify(msg="ok", value=value)


@Server.app.route("/api/webservice-dictionary/v1/complete/", methods=["GET"])
def complete() -> Response:
    dictionary = Server.complete()
    return jsonify(dictionary)


if __name__ == "__main__":
    Server.app.run(host="0.0.0.0")
