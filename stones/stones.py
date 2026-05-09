import datetime
import pathlib

from flask import Flask, render_template, request, jsonify

from . import weightdb

app = Flask(__name__)
app.debug = True
app.config.from_prefixed_env("STONES")

for k, v in app.config.items():
    print(f"{k} = {v}")

DBNAME = pathlib.Path(app.root_path).parent / "db" / "weight.db"


def use_remote_auth() -> bool:
    return app.config.get("REMOTE_AUTH") or False


def get_user() -> str | None:
    if use_remote_auth():
        return request.headers.get("Remote-User")
    return request.args.get("who")


@app.route("/")
def index():
    return render_template("index.html", user=get_user(), remote_auth=use_remote_auth())


@app.route("/weight/add")
def weight_add():
    who = get_user()

    if who is None:
        return jsonify({"status": False}), 401

    weight = request.args["weight"]
    when = request.args["when"]

    try:
        when = datetime.datetime.strptime(when, "%m/%d/%Y %I:%M %p")

        db = weightdb.WeightDb(DBNAME)
        db.add_weight(who, weight, when)

    except Exception:
        return jsonify({"status": False})

    return jsonify({"status": True})


@app.route("/weight/get/all")
@app.route("/weight/get/<int:days>")
def weight_get(days=None):
    who = get_user()

    if who is None:
        return jsonify({}), 401

    db = weightdb.WeightDb(DBNAME)
    wh = weightdb.WeightHistory(who, db, days)
    return jsonify(wh.dict_all())
