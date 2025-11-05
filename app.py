from flask import Flask, render_template, jsonify
import pandas as pd
import pandas_ta as ta
import configparser
from datetime import datetime
from delta_rest_client import DeltaRestClient

app = Flask(__name__)

def get_chart_data():
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['api']['key']
    api_secret = config['api']['secret']
    base_url = "https://api.india.delta.exchange"
    client = DeltaRestClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url
    )

    symbol = config['trading']['symbol']
    timeframe = config['trading']['timeframe']
    candle_limit = config.getint('chart', 'candle_limit')

    end_time = int(datetime.now().timestamp())
    start_time = end_time - (candle_limit * get_timeframe_seconds(timeframe))

    query_params = {
        'symbol': symbol,
        'resolution': timeframe,
        'start': start_time,
        'end': end_time
    }

    response = client.request(
        method='GET',
        path='/v2/history/candles',
        query=query_params
    )

    data = response.json()
    candles = data['result']
    df = pd.DataFrame(candles)

    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]

    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.sort_index(inplace=True)

    # Calculate indicators
    show_sma = config.getboolean('indicators', 'show_sma')
    show_supertrend = config.getboolean('indicators', 'show_supertrend')
    atr_period = config.getint('indicators', 'atr_period')
    atr_multiplier = config.getfloat('indicators', 'atr_multiplier')

    if show_sma:
        df.ta.sma(length=20, append=True, col_names=('SMA20',))
        df.ta.sma(length=50, append=True, col_names=('SMA50',))

    if show_supertrend:
        st = df.ta.supertrend(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            length=atr_period,
            multiplier=atr_multiplier
        )
        df['Supertrend'] = st[f'SUPERT_{atr_period}_{atr_multiplier}']
        df['Supertrend_Direction'] = st[f'SUPERTd_{atr_period}_{atr_multiplier}']

    return df

def get_timeframe_seconds(timeframe):
    unit = timeframe[-1]
    value = int(timeframe[:-1])

    if unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    return 60

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    df = get_chart_data()
    return jsonify(df.to_json(orient='split'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
