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
# Bscscan & Eth API
BINANCE_API_KEY = 'QAM1FFIJCJBSQAC3E3J6TXHB3KJVMM4ZJY'
ETH_API_KEY = 'VQ2TF3GG3XT5BHM897WBK6R3JTVIBARFN1'
bsc = BscScan(BINANCE_API_KEY)
chain = {'bsc': bsc}

auto_reward_list = {'SAFEMOON': ['0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3', 'bsc'],
                    'BabyDoge': ['0xc748673057861a797275CD8A068AbB95A902e8de', 'bsc']}

# SAMPLE ADDRESS AND CONTRACT TO PLAY WITH

add_1 = "0x7b30F1176949c30F9F571195EB145F2cE5C3AFA1"
add_2 = "0x3fB5DF2Da721780484B0d578f3790B130ffD9cf6"
cont = '0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3'


# This function retrieve the token amount of a wallet for a given contract


def get_token_balance_from_contract(contract, address, network):
    if network not in ['bsc', 'ethereum']:
        raise ValueError('Wrong Network')
    else:
        api = chain[network]
        if network == 'bsc':
            token = api.get_acc_balance_by_token_contract_address(contract_address=contract, address=address)
        else:
            token = api.get_acc_balance_by_token_and_contract_address(contract_address=contract, address=address)
        token_amount = {'value': float(token)/10**9, 'contract': contract, 'network': network, 'log_time': datetime.now().timestamp()}
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
    lst = [{'symbol': x['currency']['symbol'], 'address': x['currency']['address'], 'network': network}
           for x in lof_balances]
    df_token_list = pd.DataFrame(lst)
    return df_token_list


def get_token_price(base_currency, quote_currency, network):
    query = """query{
                ethereum(network: %s) {
                 dexTrades(
                 exchangeName: {in: ["Pancake", "Pancake v2"]}
                 baseCurrency: {is: %s}
                 quoteCurrency: {is: %s}) 
                 {
                 baseCurrency {
                 symbol
                 address
                 }
                 quoteCurrency {
                 symbol
                 address
                 }
                 close_price: maximum(of: block, get: quote_price)
                 quotePrice
                 }
                }     
            } 
            """
    query_pass = query % (f'{network}', f'"{base_currency}"', f'"{quote_currency}"')
    result = run_query(query_pass)  # Execute the query
    close_price = result['data']['ethereum']['dexTrades'][0]['close_price']
    return close_price


def add_token_from_user(user):
    # retrieve user auto reward tokens
    lof_values = [get_token_balance_from_contract(contract=x[0], address=user.address, network=x[1])
                  for x in list(auto_reward_list.values())]
    lof_token = [x for x in lof_values if x['value']]
    # TODO PUT LOWER CASE AND KEY VALUE
    # if there are auto tokens add them to database and record values
    for token_to_add in lof_token:
        contract = token_to_add['contract'].lower()
        record = {'value': token_to_add['value'], 'log_time': token_to_add['log_time']}
        network = token_to_add['network']
        # do user has this contract ?
        is_token = Token.query.filter((Token.contract == contract) & (Token.user_id == user.id)).all()
        if len(is_token) == 0:
            logging.info(msg=f'Adding contract: {contract} from user: ' + '<User {}>'.format(user.address))
            db.session.add(Token(contract=contract, record=record, network=network, user=user))
            db.session.commit()
        else:
            t = is_token[0]
            logging.info(msg='<Token {}>'.format(t.contract) + '<on network {}>'.format(t.network) + ' already found from user: ' + '<User {}>'.format(user.address))


# get user address and a token, return token metrics if he hold it
def get_user_metrics(address, sym):
    # get token contract
    contract = auto_reward_list.get(sym)[0].lower()
    address = address.lower()
    u = User.query.filter(User.address == address).all()[0]
    print(Token.query.all)
    is_token = Token.query.filter((Token.contract == contract) & (Token.user_id == u.id)).all()
    metrics = {'sym': sym, 'balance': 0, 'returns': 0, 'rewards': 0, 'time': 0, 'usd_rewards': 0, 'usd_balance': 0}
    if len(is_token) > 0:
        t = is_token[0]
        balance = round(get_token_balance_from_contract(contract=t.contract,
                                                        address=address,
                                                        network=t.network)['value'], 3)
        # '0xe9e7cea3dedca5984780bafc599bd69add087d56' is BUSD
        price = get_token_price(base_currency=contract, quote_currency='0xe9e7cea3dedca5984780bafc599bd69add087d56', network="bsc")
        record = t.record['value']
        log_time = t.record['log_time']
        metrics['sym'] = sym
        metrics['balance'] = balance
        metrics['returns'] = round(100*(balance-record)/record, 7)
        metrics['rewards'] = round(balance-record, 3)
        metrics['usd_rewards'] = round(metrics['rewards']*float(price), 3)
        metrics['time'] = str(datetime.now() - datetime.fromtimestamp(log_time)).split('.')[0]
        metrics['usd_balance'] = round(balance*float(price), 3)
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