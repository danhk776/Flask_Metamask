import numpy as np
import web3.eth
from flask import Flask, render_template, request, jsonify
from flask_web3 import current_web3, FlaskWeb3
from web3 import Web3
import requests
import pandas as pd
from bscscan import BscScan
from datetime import datetime
from appli import app, db
from appli.models import User, Token


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Token': Token}

# Graphql api key
GRAPHQL_API_KEY = 'BQYxXz9f04xxLN3Qirs7bnkghtWK5OBn'

# Bscscan API
BINANCE_API_KEY = 'QAM1FFIJCJBSQAC3E3J6TXHB3KJVMM4ZJY'
bsc = BscScan(BINANCE_API_KEY)
chain = {'bsc': bsc}

auto_reward_list = ['SAFEMOON']

# SAMPLE ADRESS AND CONTRACT TO PLAY WITH

add_1 = "0x7b30F1176949c30F9F571195EB145F2cE5C3AFA1"
add_2 = "0x3fB5DF2Da721780484B0d578f3790B130ffD9cf6"
cont = '0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3'


# This function retrieve the token amount of a wallet for a given contract


def get_token_balance_from_contract(contract, address, network):
    if network != 'bsc':
        raise ValueError('Wrong Network')
    else:
        api = chain[network]
        token = api.get_acc_balance_by_token_contract_address(contract_address=contract, address=address)
        token_amount = {'value': float(token)/10**9, 'log_time': datetime.now()}
        return token_amount


def run_query(qry):  # A simple function to use requests.post to make the API call.
    headers = {'X-API-KEY': GRAPHQL_API_KEY}
    req = requests.post('https://graphql.bitquery.io/', json={'query': qry}, headers=headers)
    if req.status_code == 200:
        return req.json()
    else:
        raise Exception('Query failed and return code is {}.      {}'.format(req.status_code,
                                                                             qry))


# The GraphQL query

# FUNCTION returns list of token hold by a given wallet


def get_token_list_from_address(address, network):
    query = """query {
                ethereum(network: %s) {
                    address(address: {is: %s}) {
                        balances {
                            currency {
                                address
                                symbol
                                tokenType
                            }
                        }
                    }
                }
                }
            """
    query_pass = query % (network, f'"{address}"')
    result = run_query(query_pass)  # Execute the query
    # TODO CHECK IF NOT ERROR
    # each item is a token description hold by wallet
    lof_balances = result['data']['ethereum']['address'][0]['balances']
    # all symbol
    # TODO LOOP ONLY ONCE
    lof_token = [(x['currency']['symbol'], x['currency']['address']) for x in lof_balances]
    df_token_list = pd.DataFrame({'symbol': [x[0] for x in lof_token], 'address': [x[1] for x in lof_token]})
    return df_token_list


# tokens = get_token_list_from_address(address=address, network=network)
# 628054573448.5906
# each item is a token description hold by wallet


requested_symbol = 'SAFEMOON'

# ? extract : contract and value


#def user_connection(address):
    # TODO CHECK IF ADDRESS IS VALID
    # TODO LOGGER NEW USER
    # is it new user ?
#    s = Session()
#    add_user(address=address, session=s)
#    df_user_tokens = get_token_list_from_address(address=address, network='bsc')
    # retrieve user auto reward tokens
#    df_auto = df_user_tokens[df_user_tokens['symbol'].isin(auto_reward_list)]
    # if there are auto tokens add them to database and record values
    #if not df_auto.empty:
    #    lof_contract = df_auto['address'].values
    #    # current balance and date for each token
    #    lof_value = [get_token_balance_from_contract(contract=x, address=address, network='bsc') for x in lof_contract]
    #    # datetime.fromtimestamp(date)
    #     u = s.query(User).filter(User.address == address)
    #    for i in np.arange(len(lof_contract)):
    #        add_token_from_user(contract=lof_contract[i], record=lof_value[i], user=u, session=s)
#    return s.query(User).filter(User.address == address).all()[0].address



