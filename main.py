import json
import time
from pathlib import Path
from typing import Optional, Dict

import flask
from flask import jsonify, Response


class Server:
    app = flask.Flask(__name__)
    # app.config["DEBUG"] = True
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
            Server._backup()
            return value

        except KeyError:
            return None

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


@Server.app.route("/api/webservice-dictionary/v1/get/<string:key>")
def get_value(key: str) -> Response:
    value = Server.get(key)
    if value is None:
        return jsonify(msg=f"no value for key '{key:s}'")

    return jsonify(value=value)


@Server.app.route("/api/webservice-dictionary/v1/set/<string:key>/<string:value>")
def set_value(key: str, value: str) -> Response:
    Server.set(key, value)
    return jsonify(msg="key mapped to value")


@Server.app.route("/api/webservice-dictionary/v1/pop/<string:key>")
def pop_value(key: str) -> Response:
    value = Server.pop(key)
    if value is None:
        return jsonify(msg=f"no value for key '{key:s}'")

    return jsonify(value=value)


@Server.app.route("/api/webservice-dictionary/v1/complete/")
def complete() -> Response:
    dictionary = Server.complete()
    return jsonify(dictionary)


if __name__ == "__main__":
    Server.app.run()
