from appli import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, request, jsonify
#from hello import get_token_balance_from_contract, get_token_list_from_address
from metamask import get_token_balance_from_contract, get_token_list_from_address, user_connection, \
    get_user_metrics


@app.route('/')
def index():
    return render_template('table copie.html')


@app.route('/table')
def table():
    return render_template('table copie.html')


# ###################


@app.route('/user_metrics', methods=['POST'])
def get_metrics_from_user():
    js_data_address = request.form['address']
    js_data_sym = request.form['sym']
    metrics = get_user_metrics(address=js_data_address, sym=js_data_sym)
    return metrics


@app.route('/connection', methods=['POST'])
def connection():
    js_data_address = request.form['address']
    user_connection(address=js_data_address)
    return "True"
