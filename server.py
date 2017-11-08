import sys
import os
sys.path.append(os.getcwd())

from flask import Flask, render_template, redirect, session, request, jsonify
from models.fact_model import FactModel, User
from models.base_model import DBSingelton
import bcrypt

app = Flask(__name__)


@app.before_first_request
def initialize_tables():
    tables = [User, FactModel]

    connect_db()
    for table in tables:
        if not table.table_exists():
            table.create_table()
    disconnect_db()


@app.before_request
def connect_db():
    DBSingelton.getInstance().connect()


@app.teardown_request
def disconnect_db(err=None):
    DBSingelton.getInstance().close()


@app.route("/facts", methods=["POST", "GET"])
def add_get_fact():
    if request.method == "POST":
        if session.get("logged_in", False):
            fact = request.form.get("fact")
            user = request.form.get("user")
            is_true = int(request.form.get("is_true"))
            new_fact = FactModel(user=user, fact=fact, is_true=is_true)
            new_fact.save()
            return jsonify({"success": "created!"}), 201
        return jsonify({"error": "forbidden!"}), 403
    results = FactModel.select().dicts()
    return jsonify({"data": list(results)})


@app.route("/facts/<int:num>", methods=["PUT", "GET", "DELETE"])
def edit_get_delete_fact(num):
    item = FactModel.get(FactModel.id == num)
    if request.method == "PUT":
        temp_dict = item._data
        for key, value in temp_dict.items():
            item._data[key] = request.form.get(key, value)
        item._data["is_true"] = int(item._data["is_true"])
        item.save()
        return jsonify({"result": "success"})
    elif request.method == "GET":
        return jsonify({"data": item._data})
    else:
        if request.method == "DELETE":
            item.delete_instance()
        return jsonify({"success": "deleted!"})


@app.route("/users", methods=["POST", "GET"])
def add_get_users():
    if request.method == "POST":
        if session.get("logged_in", False):
            name = request.form.get("name")
            password = bcrypt.hashpw(
                request.form.get("password").encode("utf-8"),
                bcrypt.gensalt())
            new_user = User(name=name, password=password)
            new_user.save()
            return jsonify({"result": "success"}), 201
        return jsonify({"error": "failure"}), 403
    else:
        users = User.select().dicts()
        return jsonify({"data": list(users)})


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    password = request.form.get("password")
    user = User.get(User.name == name)._data

    session["logged_in"] = bcrypt.checkpw(
        password.encode("utf-8"), user["password"].encode("utf-8"))
    if session["logged_in"]:
        return jsonify({"result": "success"})
    return jsonify({"error": "Login failed!"})

app.secret_key = os.environ.get("FLASK_SECRET_KEY")
