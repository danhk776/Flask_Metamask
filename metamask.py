import time

import celery
import numpy as np
import requests
import pandas as pd
from bscscan import BscScan
from datetime import datetime
from appli import app, db
from appli.models import User, Token
import logging


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Token': Token}


logging.basicConfig(level=logging.INFO)
# Graphql api key
GRAPHQL_API_KEY = 'BQYxXz9f04xxLN3Qirs7bnkghtWK5OBn'
_GLOB = 1
# Bscscan API
BINANCE_API_KEY = 'QAM1FFIJCJBSQAC3E3J6TXHB3KJVMM4ZJY'
bsc = BscScan(BINANCE_API_KEY)
chain = {'bsc': bsc}

auto_reward_list = {'SAFEMOON': '0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3',
                     'FEG': '0xacfc95585d80ab62f67a14c566c1b7a49fe91167',
                    'SAFEMARS': '0x3ad9594151886ce8538c1ff615efa2385a8c3a88',
                    'SAFEBTC': '0x380624a4a7e69db1ca07deecf764025fc224d056',
                    'FOX': '0xfad8e46123d7b4e77496491769c167ff894d2acb',
                    'OCTA': '0x86c3e4ffacdb3af628ef985a518cd6ee22a22b28'}

# SAMPLE ADDRESS AND CONTRACT TO PLAY WITH

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
        token_amount = {'value': float(token)/10**9, 'log_time': datetime.now().timestamp()}
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
                            }
                        }
                    }
                }
                }
            """
    query_pass = query % (network, f'"{address}"')
    result = run_query(query_pass)  # Execute the query
    if 'errors' in result.keys():
        raise ValueError(result['errors'][0]['message'])
    # each item is a token description hold by the wallet
    lof_balances = result['data']['ethereum']['address'][0]['balances']
    lst = [{'symbol': x['currency']['symbol'], 'address': x['currency']['address']}
           for x in lof_balances]
    df_token_list = pd.DataFrame(lst)
    return df_token_list


def add_token_from_user(user):
    df_user_tokens = get_token_list_from_address(address=user.address, network='bsc')
    # retrieve user auto reward tokens
    # TODO PUT LOWER CASE AND KEY VALUE
    df_auto = df_user_tokens[df_user_tokens['symbol'].isin(auto_reward_list.keys())]
    # if there are auto tokens add them to database and record values

    if not df_auto.empty:
        # lof_contract = sorted(df_auto['address'].values, key=list(auto_reward_list.values()).index)
        lof_contract = df_auto['address'].values
        lof_value = [get_token_balance_from_contract(contract=x, address=user.address, network='bsc')
                     for x in lof_contract]
        for i in np.arange(len(lof_contract)):
            # do user has this contract ?
            contract = lof_contract[i]
            record = lof_value[i]
            is_token = Token.query.filter((Token.contract == contract) & (Token.user_id == user.id)).all()
            if len(is_token) == 0:
                logging.info(msg=f'Adding contract: {contract} from user: ' + '<User {}>'.format(user.address))
                db.session.add(Token(contract=contract, record=record, user=user))
                db.session.commit()
            else:
                t = is_token[0]
                logging.info(msg='<Token {}>'.format(t.contract) + ' already found from user: ' + '<User {}>'.format(user.address))

    else:
        logging.info('no safe token found')


# get user address and a token return token metrics if he has it
def get_user_metrics(address, sym):
    # get token contract
    contract = auto_reward_list.get(sym).lower()
    address = address.lower()
    u = User.query.filter(User.address == address).all()[0]
    is_token = Token.query.filter((Token.contract == contract) & (Token.user_id == u.id)).all()
    metrics = {'balance': 0, 'returns': 0, 'rewards': 0, 'time': 0}
    if len(is_token) > 0:
        t = is_token[0]
        balance = round(get_token_balance_from_contract(contract=t.contract,
                                                        address=address,
                                                        network='bsc')['value'], 3)
        record = t.record['value']
        log_time = t.record['log_time']
        metrics['balance'] = balance
        metrics['returns'] = round(100*(balance-record)/record, 7)
        metrics['rewards'] = round(balance-record, 3)
        metrics['time'] = str(datetime.now() - datetime.fromtimestamp(log_time))
    return metrics


def add_user(address):
    is_exist = User.query.filter(User.address == address).all()
    # if user does not exist add him
    if len(is_exist) == 0:
        u = User(address=address)
        logging.info(msg=f'New user detected' + '<User {}>'.format(u.address))
        db.session.add(u)
        db.session.commit()
    else:
        u = is_exist[0]
        logging.info(msg=f'User detected in the database : ' + '<User {}>'.format(u.address))
    return u


def user_connection(address):
    # TODO CHECK IF ADDRESS IS VALID
    # USER REGISTRATION PART
    u = add_user(address=address)
    # #########################

    # TOKEN USER REGISTRATION PART
    add_token_from_user(user=u)
    # #########################