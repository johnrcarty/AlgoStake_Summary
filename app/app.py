import dash
from dash import Dash, Input, Output, callback, dash_table, html, dcc
import dash_bootstrap_components as dbc

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go

import requests
import pandas as pd
import datetime
import pytz
import os
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from dateutil.relativedelta import *
from sqlalchemy import create_engine
import numpy as np

load_dotenv()

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

RDS_CERT_PATH = "/test-ca-certificate.crt"
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}?sslmode=require"

Watch_List = ['SSV6SKTMN3IOJO6SWUAT5ERZOBC5K44CQPOH5O7NSXJLGFGU73WUQ7DPGA',
              '4ZK3UPFRJ643ETWSWZ4YJXH3LQTL2FUEI6CIT7HEOVZL6JOECVRMPP34CY',
              'FAUC7F2DF3UGQFX2QIR5FI5PFKPF6BPVIOSN2X47IKRLO6AMEVA6FFOGUQ']

args = {
    'sslrootcert': RDS_CERT_PATH
}
engine = create_engine(DATABASE_URL,
                       connect_args=args)

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}
# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

controls = dbc.FormGroup(
    [

        html.P('Wallet', style={
            'textAlign': 'center'
        }),
        dcc.Input(
            id="wallet_id",
            type="text",
            placeholder="Algorand Public Address",
        ),
        html.Br(),
        html.Br(),
        html.P('Asset', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='dropdown',
            options=[],
            value=[],  # default value
            multi=True
        ),
        html.Br(),
        # html.P('Range Slider', style={
        #     'textAlign': 'center'
        # }),
        # dcc.RangeSlider(
        #     id='range_slider',
        #     min=0,
        #     max=20,
        #     step=0.5,
        #     value=[5, 15]
        # ),
        # html.P('Check Box', style={
        #     'textAlign': 'center'
        # }),
        # dbc.Card([dbc.Checklist(
        #     id='check_list',
        #     options=[{
        #         'label': 'Value One',
        #         'value': 'value1'
        #     },
        #         {
        #             'label': 'Value Two',
        #             'value': 'value2'
        #         },
        #         {
        #             'label': 'Value Three',
        #             'value': 'value3'
        #         }
        #     ],
        #     value=['value1', 'value2'],
        #     inline=True
        # )]),
        html.Br(),
        html.P('Radio Items', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.RadioItems(
            id='radio_items',
            options=[{
                'label': 'Asset Total',
                'value': 'total'
            },
                {
                    'label': 'Algo Amount',
                    'value': 'algo_total'
                },
                {
                    'label': 'USD Amount',
                    'value': 'usd_total'
                }
            ],
            value='total',
            style={
                'margin': 'auto'
            }
        )]),
        html.Br(),
        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Submit',
            color='primary',
            block=True
        ),
    ]
)

sidebar = html.Div(
    [
        html.H2('Parameters', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

content_first_row = dbc.Row([
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(id='card_title_1', children=['AlgoStake Rewards'], className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_1', children=[''], style=CARD_TEXT_STYLE),
                    ]
                )
            ]
        ),
        md=4
    ),
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(id='card_title_2', children=['Current Value in ALGO'], className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_2', children=[''], style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=4
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(id='card_title_3', children=['Current Value in USD'], className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_3', children=[''], style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=4
        # ),
        # dbc.Col(
        #     dbc.Card(
        #         [
        #             dbc.CardBody(
        #                 [
        #                     html.H4('Card Title 4', className='card-title', style=CARD_TEXT_STYLE),
        #                     html.P('Sample text.', style=CARD_TEXT_STYLE),
        #                 ]
        #             ),
        #         ]
        #     ),
        #     md=3
    )
])

content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1'), md=12
        )
    ]
)

content_third_row = dbc.Row(
    [
        dbc.Col(
            dbc.Table(id='asset_tbl'), md=12,
        )
    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(

        )
    ]
)

content = html.Div(
    [
        html.H2('AlgoStake Reward Summary', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_second_row,
        content_third_row,
        # content_fourth_row,
    ],
    style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])
server = app.server


# @app.callback(
#     Output('graph_1', 'figure'),
#     [Input('submit_button', 'n_clicks')],
#     [State('dropdown', 'value'), State('wallet_id', 'value')])
# def update_graph_1(n_clicks, dropdown_value, wallet_id_value):
#     # print(n_clicks)
#     # print(dropdown_value)
#     # print(range_slider_value)
#     # print(check_list_value)
#     # print(radio_items_value)
#     fig = {
#         'data': [{
#             'x': [1, 2, 3],
#             'y': [3, 4, 5]
#         }]
#     }
#     return fig


@app.callback(
    Output('card_title_1', 'children'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('wallet_id', 'value'), State('radio_items', 'value')])
def update_card_title_1(n_clicks, dropdown_value, wallet_id_value, radio_items_value):
    print(radio_items_value)
    if radio_items_value == 'total':
        return 'Assets Received'
    elif radio_items_value == 'algo_total':
        return 'Value in ALGO Received'
    elif radio_items_value == 'usd_total':
        return 'Value in USD Received'
    else:
        return 'Asset Summary'


@app.callback(
    [Output('asset_tbl', 'children'), Output('dropdown', 'options'), Output('card_text_1', 'children'),
     Output('card_text_2', 'children'), Output('card_text_3', 'children'), Output('graph_1', 'figure')],
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('wallet_id', 'value'), State('radio_items', 'value')])
def update_card_text_1(n_clicks, dropdown_value, wallet_id_value, radio_items_value):
    url = 'https://free-api.vestige.fi/asset/900652777/price'
    r = requests.get(url)
    response = r.json()
    current_algo = response['price']
    current_usd = response['USD']

    if wallet_id_value == "" or wallet_id_value is None:
        raise PreventUpdate
    else:
        check_update_qry = f"""select coalesce(max(timestamp_utc), '1900-01-01') > date_trunc('month', current_date) as current_data   
                                , coalesce(max(timestamp_utc), '1900-01-01') last_date
                                from staking_transactions
                                where receiver = '{wallet_id_value}'"""
        check_update_res = pd.read_sql(check_update_qry, engine)
        current_data = check_update_res.iloc[0, 0]
        last_date = check_update_res.iloc[0, 1]
        print(f'last date: {last_date}')
        if not current_data:
            update_db(wallet_id_value, last_date)

    trans_data = get_table(wallet_id_value, radio_items_value)
    print(len(trans_data))
    total = round(sum(trans_data[trans_data['name'] == 'AlgoStake']['total']), 4)
    total_algo = round(total * current_algo, 4)
    total_usd = round(total * current_usd, 4)
    options = [{'label': i, 'value': i} for i in trans_data['name'].unique()]
    trans_data['short_date'] = trans_data['month_end'].apply(
        lambda x: datetime.strptime(str(x), '%Y-%m-%d').strftime('%b-%y'))

    if dropdown_value:
        trans_data = trans_data[trans_data['name'].isin(dropdown_value)]

    trans_data = trans_data.sort_values(by='month_end', ascending=True)
    months = [{'month_end': i, 'short_date': datetime.strptime(str(i), '%Y-%m-%d').strftime('%b-%y')}
              for i in trans_data['month_end'].unique()]
    months = (pd.DataFrame(months))

    data = trans_data.pivot(index='name', columns='short_date', values='total')
    data.reset_index(inplace=True)

    if radio_items_value == 'total':
        fig2_data = data.agg(['count'])
        total = len(trans_data['name'].unique())

    elif radio_items_value == 'algo_total':
        fig2_data = data.agg(['sum'])
        total = round(sum(trans_data['total']), 4)

    elif radio_items_value == 'usd_total':
        fig2_data = data.agg(['sum'])
        total = round(sum(trans_data['total']), 4)

    else:
        fig2_data = data.agg(['sum'])
        total = round(sum(trans_data['total']), 4)

    fig2_data.drop('name', axis=1, inplace=True)
    unique_months = list(months['short_date'].unique())
    fig2_data = fig2_data[unique_months]
    print(fig2_data.columns)
    # fig2_data = pd.DataFrame(data.sum(numeric_only=True))
    unique_months.insert(0, 'name')
    fig = dbc.Table.from_dataframe(data[unique_months], striped=True, bordered=True, hover=True)
    fig2 = {
        'data': [{
            'x': list(fig2_data.columns),
            'y': fig2_data.iloc[0].tolist()
        }]
    }
    return [fig, options, str(total), str(total_algo), str(total_usd), fig2]


def update_db(wallet_id, start_date):
    print(f'Updating Wallet: {wallet_id}\nBeggining: {start_date}')
    get_transactions(wallet_id, start_date)


def get_table(sender, radio_value):
    tbl_qry = f"""select a.name, a.index
                            , (date_trunc('month', s.timestamp_utc) + interval '1 month - 1 day')::date month_end
                            , sum(case 
                                    when a.decimals = 0 then s.amount 
                                    else s.amount / 10 ^ a.decimals end) as total
                        from staking_transactions s
                        join assets a on a.index = s.asset_id

                        where s.receiver = '{sender}'

                        group by a.name, a.index
                                , (date_trunc('month', s.timestamp_utc) + interval '1 month - 1 day')::date"""
    df = pd.read_sql(tbl_qry, engine)
    df_len = len(df)
    if df_len == 0:
        return pd.DataFrame()
    assets = df['index'].unique()
    asset_list = []
    for asset in assets:
        asset_list.append(get_prices(asset))
    df_2 = pd.DataFrame(asset_list)
    # print(df['index'].apply(lambda x: get_prices(x)))
    df_3 = df.merge(df_2, right_on='index', left_on='index')
    df_3['algo_total'] = df_3['total'] * df_3['algo']
    df_3['usd_total'] = df_3['total'] * df_3['usd']
    df_final = df_3[['name', 'month_end', radio_value]]
    col_names = {
        radio_value: 'total'
    }
    df_final.rename(columns=col_names, inplace=True)
    df_final['total'] = df_final['total'].apply(lambda x: round(x, 4))
    return df_final


def get_prices(asset_id):
    asset_str = str(asset_id).replace('.0', '')
    url = f'https://free-api.vestige.fi/asset/{asset_str}/price'
    r = requests.get(url)
    response = r.json()

    return {'index': asset_id, 'algo': response['price'], 'usd': response['USD']}


def load_transactions(trx, trx_clean=[]):
    asset_qry = f"select index from assets"
    asset_list = pd.read_sql(asset_qry, engine)
    block_qry = f"select * from block_time"
    block_list = pd.read_sql(block_qry, engine)

    i = 0
    for t in trx:
        progbar(i,len(trx),20)
        i = i + 1
        
        if 'sender' in t:
            sender = t['sender']
        else:
            sender = 'missing'

        if 'confirmed-round' in t:
            block = t['confirmed-round']
        else:
            block = 'missing'

        if 'id' in t:
            tx_id = t['id']
        else:
            tx_id = 'missing'

        if sender in Watch_List:
            if "asset-transfer-transaction" in t:
                tmp = t['asset-transfer-transaction']
                tmp['sender'] = sender
                tmp['block'] = block
                tmp['tx_id'] = tx_id
                asset_id = tmp['asset-id']
                if asset_id not in asset_list['index'].unique():
                    asset_list = check_asset(asset_id)
                if block not in block_list['round_number'].unique():
                    block_list = check_block(block)
                trx_clean.append(tmp)
                
    df = pd.DataFrame(data=trx_clean)
    small_block = block_list[['round_number', 'timestamp_utc']]
    df_2 = df.merge(small_block, left_on="block", right_on="round_number")
    col_names = {'amount': "amount",
                 'asset-id': "asset_id",
                 'close-amount': "close_amount",
                 'receiver': "receiver",
                 'sender': "sender",
                 'block': "block",
                 'tx_id': "tx_id",
                 "round_number": "round_number",
                 "timestamp_utc": "timestamp_utc"
                 }
    col_order = ['receiver', 'sender', 'block', 'tx_id', 'asset_id', 'amount', 'close_amount', "timestamp_utc"]
    df_2.rename(columns=col_names, inplace=True)
    df_2 = df_2[col_order]
    df_2.to_sql('staking_transactions', engine, if_exists='append', index=False)
    return trx_clean


def get_transactions(addr, start_date):
    today = date.today()
    end_date = today.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4] + "Z"
    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4] + "Z"
    url = 'https://algoindexer.algoexplorerapi.io/v2/accounts/'
    url = url + f'{addr}/transactions?before-time={end_date}&after-time={start_date}'
    print(url)
    headers = {'accept': 'application/json'}
    r = requests.get(url, headers=headers)
    response = r.json()
    trx = response['transactions']
    transactions_clean = load_transactions(trx)
    while 'next-token' in response:
        next_id = response['next-token']
        url = f'https://algoindexer.algoexplorerapi.io/v2/accounts/{addr}/transactions?next={next_id}'
        r = requests.get(url, headers=headers)
        response = r.json()
        trx = response['transactions']
        transactions_clean = load_transactions(trx, transactions_clean)

    return transactions_clean


def progbar(curr, total, full_progbar):
    frac = curr / total
    filled_progbar = round(frac * full_progbar)
    print('\r', '#' * filled_progbar + '-' * (full_progbar - filled_progbar), '[{:>7.2%}]'.format(frac), end='')



def check_asset(asset_id):
    asset_url = f'https://algoindexer.algoexplorerapi.io/v2/assets/{asset_id}'
    headers = {'accept': 'application/json'}
    response = requests.get(asset_url, headers=headers).json()
    asset = response['asset']
    asset_2 = pd.json_normalize(asset)
    cols = {'created-at-round': 'created_at_round',
            'params.clawback': 'clawback',
            'params.creator': 'creator',
            'params.decimals': 'decimals',
            'params.default-frozen': 'default_frozen',
            'params.freeze': 'freeze',
            'params.manager': 'manager',
            'params.name': 'name',
            'params.name-b64': 'name_b64',
            'params.reserve': 'reserve',
            'params.total': 'total',
            'params.unit-name': 'unit_name',
            'params.unit-name-b64': 'unit_name_b64',
            'params.url': 'url',
            'params.url-b64': 'url_b64'}
    col_order = ['index', 'created_at_round', 'deleted', 'name', 'name_b64',
                 'creator', 'manager', 'reserve', 'clawback', 'freeze', 'default_frozen',
                 'total', 'decimals', 'unit_name', 'unit_name_b64', 'url', 'url_b64']
    asset_2.rename(columns=cols, inplace=True)
    for col in col_order:
        if col not in asset_2.columns:
            asset_2[col] = ''
    asset_final = asset_2[col_order]
    asset_final['total'] = asset_final['total'].apply(str)
    asset_final.to_sql('assets', engine, if_exists='append', index=False)
    asset_final['created_at_round'].apply(lambda x: check_block(x))

    qry = f"select index from assets"
    return pd.read_sql(qry, engine)


def check_block(block_id):
    block_url = f"https://algoindexer.algoexplorerapi.io/v2/blocks/{block_id}"
    headers = {'accept': 'application/json'}
    response = requests.get(block_url, headers=headers).json()
    timestamp = datetime.fromtimestamp(response['timestamp'], tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    d = {'round_number': block_id, 'timestamp_utc': [timestamp]}
    df = pd.DataFrame(data=d)
    df.to_sql('block_time', engine, if_exists='append', index=False)
    # Block_List[block_id] = params

    block_qry = f"select * from block_time"
    return pd.read_sql(block_qry, engine)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8050", debug=True)
