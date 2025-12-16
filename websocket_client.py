import websocket
import json
import threading
import time

def on_message(ws, message, socketio, symbol, timeframe, supertrend_calculator):
    data = json.loads(message)
    if data.get('type') == f'candlestick_{timeframe}' and data.get('symbol') == symbol:
        new_candle = {
            'high': data['high'],
            'low': data['low'],
            'close': data['close']
        }
        supertrend, direction = supertrend_calculator.update(new_candle)
        data['supertrend'] = supertrend
        data['direction'] = direction
        socketio.emit('new_candle', data)

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed with status: {close_status_code} and message: {close_msg}")

def on_open(ws, timeframe, symbol):
    def run(*args):
        subscribe_message = {
            "type": "subscribe",
            "payload": {
                "channels": [
                    {
                        "name": f"candlestick_{timeframe}",
                        "symbols": [symbol]
                    }
                ]
            }
        }
        ws.send(json.dumps(subscribe_message))
    threading.Thread(target=run).start()

def start_websocket(socketio, timeframe, symbol, supertrend_calculator):
    ws = websocket.WebSocketApp(
        "wss://socket.delta.exchange",
        on_open=lambda ws: on_open(ws, timeframe, symbol),
        on_message=lambda ws, msg: on_message(ws, msg, socketio, symbol, timeframe, supertrend_calculator),
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
