from appli import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, request, jsonify
#from hello import get_token_balance_from_contract, get_token_list_from_address
from metamask import get_token_balance_from_contract, get_token_list_from_address, user_connection, \
    get_user_token_balance


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/table')
def table():
    return render_template('table copie.html')


@app.route('/postmethod', methods=['POST'])
def get_post_javascript_data():
    js_data = int(request.form['javascript_data'], 0) + 1
    return {'val': js_data}

# ####################


@app.route('/token_list', methods=['POST'])
def return_token_list_from_balance():
    js_data = request.form['address']
    lof_tokens = get_token_list_from_address(address=js_data, network='bsc')
    print(lof_tokens['symbol'].values)
    return {'lof_tokens': lof_tokens['symbol'].values}


@app.route('/token_balance', methods=['POST'])
def return_token_balance_from_address():
    js_data_address = request.form['address']
    metrics = get_user_token_balance(address=js_data_address)
    lof_balance = metrics['balances']
    apy = metrics['apy']
    rewards = metrics['rewards']
    staking_time = metrics['staking_time']
    return {"balances": lof_balance, 'apy': apy, 'rewards': rewards, 'staking_time': staking_time}


@app.route('/connection', methods=['POST'])
def connection():
    js_data_address = request.form['address']
    user_connection(address=js_data_address)
    return "True"
