import sys
import os
sys.path.append(os.getcwd())

from flask import Flask, render_template, redirect, session, request, url_for, jsonify
from models.fact_model import FactModel
from models.base_model import DBSingelton

app = Flask(__name__)


def listify(objects):
    obj_list = [item._data for item in objects]
    return obj_list


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


@app.route("/facts/new", methods=["POST", "GET"])
def add_fact():
    if request.method == "POST":
        fact = request.form.get("fact")
        user = request.form.get("user")
        is_true = int(request.form.get("is_true"))
        new_fact = FactModel(user=user, fact=fact, is_true=is_true)
        new_fact.save()
        return redirect(url_for("get_facts"))
    return render_template("new_fact.html")


@app.route("/facts/<int:num>", methods=["GET"])
def get_fact(num):
    result = FactModel.select().where(FactModel.id == num).get()
    # return render_template("fact.html", result=result)
    return jsonify(result._data)


@app.route("/facts", methods=["GET"])
def get_facts():
    results = FactModel.select()
    # return render_template("facts.html", results=results)
    return jsonify(listify(results))


app.secret_key = os.environ.get("FLASK_SECRET_KEY")
