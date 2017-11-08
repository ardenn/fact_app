import sys
import os
sys.path.append(os.getcwd())

from flask import Flask, render_template, redirect, session, request, url_for, jsonify
from models.fact_model import FactModel
from models.base_model import DBSingelton

app = Flask(__name__)


@app.before_first_request
def initialize_tables():
    connect_db()
    if not FactModel.table_exists():
        FactModel.create_table()
    disconnect_db()


@app.before_request
def connect_db():
    DBSingelton.getInstance().connect()


@app.teardown_request
def disconnect_db(err=None):
    DBSingelton.getInstance().close()


@app.route("/facts", methods=["POST"])
def add_fact():
    if request.method == "POST":
        fact = request.form.get("fact")
        user = request.form.get("user")
        is_true = int(request.form.get("is_true", 0))
        new_fact = FactModel(user=user, fact=fact, is_true=is_true)
        new_fact.save()
        return jsonify({"result": "success"})


@app.route("/facts/<int:num>", methods=["PUT"])
def edit_fact(num):
    item = FactModel.get(FactModel.id == num)
    if request.method == "PUT":
        temp_dict = item._data
        print(temp_dict)
        for key, value in temp_dict.items():
            item._data[key] = request.form.get(key, value)
        item._data["is_true"] = int(item._data["is_true"])
        item.save()
    return jsonify({"result": "success"})


@app.route("/facts/<int:num>", methods=["GET"])
def get_fact(num):
    result = FactModel.select().where(FactModel.id == num).get()
    return jsonify({"data": result._data})


@app.route("/facts", methods=["GET"])
def get_facts():
    results = FactModel.select().dicts()
    return jsonify({"data": list(results)})


@app.route("/facts/<int:num>", methods=["DELETE"])
def delete_fact(num):
    item = FactModel.get(FactModel.id == num)
    if request.method == "DELETE":
        item.delete_instance()
        return jsonify({"result": "success"})

app.secret_key = os.environ.get("FLASK_SECRET_KEY")
