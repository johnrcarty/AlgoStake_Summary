from dash import Dash, Input, Output, callback, dash_table, html, dcc
import requests
import pandas as pd
import datetime
from datetime import datetime
from dateutil.relativedelta import *

Trx_Summary = []

Watch_List = ['SSV6SKTMN3IOJO6SWUAT5ERZOBC5K44CQPOH5O7NSXJLGFGU73WUQ7DPGA',
              '4ZK3UPFRJ643ETWSWZ4YJXH3LQTL2FUEI6CIT7HEOVZL6JOECVRMPP34CY']

Block_List = {}

Asset_List = {}

Transactions_Clean = []


def get_transactions(addr, start_date, end_date):
    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4] + "Z"
    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4] + "Z"
    print(start_date)
    print(end_date)
    url = 'https://algoindexer.algoexplorerapi.io/v2/accounts/'
    url = url + f'{addr}/transactions?before-time={end_date}&after-time={start_date}'
    headers = {'accept': 'application/json'}
    r = requests.get(url, headers=headers)
    response = r.json()
    trx = response['transactions']
    while 'next-token' in response:
        next_id = response['next-token']
        url = f'https://algoindexer.algoexplorerapi.io/v2/accounts/{addr}/transactions?next={next_id}'
        r = requests.get(url, headers=headers)
        response = r.json()
        tmp_trx = response['transactions']
        trx = trx + tmp_trx
    trx_clean = []
    for t in trx:
        sender = t['sender']
        block = t['confirmed-round']

        if sender in Watch_List:
            if "asset-transfer-transaction" in t:
                tmp = t['asset-transfer-transaction']
                tmp['sender'] = sender
                check_asset(tmp['asset-id'])
                check_block(block)
                tmp['asset-name'] = Asset_List[tmp['asset-id']]['name']
                tmp['asset-decimals'] = Asset_List[tmp['asset-id']]['decimals']
                tmp['timestamp'] = Block_List[block]['timestamp']
                tmp['month'] = Block_List[block]['month']
                Transactions_Clean.append(tmp)
    return trx_clean


def check_asset(asset_id):
    if asset_id not in Asset_List:
        asset_url = f'https://algoindexer.algoexplorerapi.io/v2/assets/{asset_id}'
        headers = {'accept': 'application/json'}
        response = requests.get(asset_url, headers=headers).json()
        asset = response['asset']['params']
        params = {'name': asset['name'], 'decimals': asset['decimals']}
        Asset_List[asset_id] = params


def check_block(block_id):
    if block_id not in Block_List:
        block_url = f"https://algoindexer.algoexplorerapi.io/v2/blocks/{block_id}"
        headers = {'accept': 'application/json'}
        response = requests.get(block_url, headers=headers).json()
        timestamp = datetime.fromtimestamp(response['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        month = datetime.fromtimestamp(response['timestamp']).replace(day=1).strftime('%Y-%m-%d')
        params = {'timestamp': timestamp, 'month': month}
        Block_List[block_id] = params


app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2('AlgoStake Monthly Summary'),
    dcc.Input(id="wallet-id", type="text", placeholder="", style={'marginRight': '10px'}),
    html.Div(id='display-value', className='wallet-box'),
    html.Div(id='tbl-div', className='tbl-div')
])


@callback([Output('display-value', 'children'),
           Output('tbl-div', 'children')],
          [Input('wallet-id', 'value')])
def display_value(value):
    if value == "" or value is None:
        return 'None'
    end_new = datetime.today().replace(day=1) + relativedelta(months=+1)
    start_new = datetime.today().replace(day=1) + relativedelta(months=-1, years=-1)
    start = start_new.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end_new.replace(hour=0, minute=0, second=0, microsecond=0)
    s = start
    e = end
    get_transactions(value, s, e)

    df = pd.DataFrame(Transactions_Clean)
    df['amount-actual'] = df['amount'] / 10 ** df['asset-decimals']
    df2 = df.groupby(['asset-name', 'month'], as_index=False).agg(Total=('amount-actual', 'sum'))
    data = df2.pivot(index='asset-name', columns='month', values='Total')
    data.reset_index(inplace=True)
    data = data.rename(columns={'index': 'Asset'})
    print(data.head())
    print(data.to_dict('records'))
    columns = []
    for c in data.columns:
        columns.append({'id': c, 'name': c})
    dt = html.Div(dash_table.DataTable(
        data.to_dict('records'),
        id='trx-table',
        columns=columns,
        editable=True,

        persistence=True,  # <---
        persisted_props=["data"]))
    div_text = f'Summary for {value}'
    return div_text, dt


if __name__ == '__main__':
    app.run_server(debug=True)
