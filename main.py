import json
import time
from pathlib import Path
from typing import Optional

import flask
from flask import jsonify, Response, request


class Server:
    app = flask.Flask(__name__)
    # app.config["DEBUG"] = True  # automatic reload on code change

    path_file = Path("backup.json")
    if path_file.is_file():
        with path_file.open(mode="r") as file:
            backup = json.load(file)
    else:
        backup = dict()

    non_tuple_keys = backup.get("non_tuple_keys")
    if non_tuple_keys is None:
        non_tuple_keys = dict()
        backup["non_tuple_keys"] = non_tuple_keys

    tuple_keys = backup.get("tuple_keys")
    if tuple_keys is None:
        tuple_keys = dict()
        backup["tuple_keys"] = tuple_keys

    time_write_last = time.time()

    @staticmethod
    def flush():
        with Server.path_file.open(mode="w") as file:
            json.dump(Server.backup, file, indent=2, sort_keys=True)

    @staticmethod
    def _backup():
        time_now = time.time()
        if 10. < time_now - Server.time_write_last:
            Server.flush()
            Server.time_write_last = time_now

    @staticmethod
    def pop(key: str, key_is_tuple: bool) -> Optional[str]:
        if key_is_tuple:
            value = Server.tuple_keys.pop(key)

        else:
            value = Server.non_tuple_keys.pop(key)

        Server._backup()
        return value

    @staticmethod
    def get(key: str, key_is_tuple: bool) -> Optional[str]:
        if key_is_tuple:
            return Server.tuple_keys.get(key)

        return Server.non_tuple_keys.get(key)

    @staticmethod
    def set(key: str, value: str, key_is_tuple: bool):
        if key_is_tuple:
            Server.tuple_keys[key] = value
        else:
            Server.non_tuple_keys[key] = value
        Server._backup()


@Server.app.route("/", methods=["GET"])
def home() -> Response:
    return jsonify(msg="<h1>Webservice Dictionary</h1><p>This site is a prototype API for a Python dictionary.</p>")


@Server.app.route("/api/webservice-dictionary/v1/set/", methods=["PUT"])
def set_value() -> Response:
    try:
        key = request.form["key"]
        value = request.form["value"]
        key_is_tuple = request.form["key_is_tuple"]

    except KeyError as e:
        return jsonify(error=str(e))

    Server.set(key, value, json.loads(key_is_tuple))
    return jsonify(msg="key mapped to value")


@Server.app.route("/api/webservice-dictionary/v1/pop/", methods=["PUT"])
def pop_value() -> Response:
    try:
        key = request.form["key"]
        key_is_tuple = request.form["key_is_tuple"]

    except KeyError as e:
        return jsonify(error=str(e))

    try:
        value = Server.pop(key, json.loads(key_is_tuple))

    except KeyError as e:
        return jsonify(error=str(e))

    return jsonify(value=value)


@Server.app.route("/api/webservice-dictionary/v1/get/", methods=["GET"])
def get_value() -> Response:
    try:
        key = request.args["key"]
        key_is_tuple = request.args["key_is_tuple"]

    except KeyError as e:
        return jsonify(error=str(e))

    value = Server.get(key, json.loads(key_is_tuple))
    if value is None:
        return jsonify(msg=f"no value for key '{key:s}'")

    return jsonify(msg="ok", value=value)


@Server.app.route("/api/webservice-dictionary/v1/complete/", methods=["GET"])
def complete() -> Response:
    return jsonify(tuple_keys=Server.tuple_keys, non_tuple_keys=Server.non_tuple_keys)


@Server.app.route("/api/webservice-dictionary/v1/flush/", methods=["PUT"])
def flush() -> Response:
    Server.flush()
    return jsonify(msg="ok")


if __name__ == "__main__":
    Server.app.run(host="0.0.0.0")
