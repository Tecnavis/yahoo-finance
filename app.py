import eventlet

eventlet.monkey_patch()

from flask import Flask, jsonify, render_template
from yahoo_fin import stock_info
from datetime import datetime
from flask_socketio import SocketIO ,emit
from dotenv import load_dotenv
import os
from flask import request

load_dotenv()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', engineio_logger=True, async_mode='eventlet')
connected_clients = 0


@app.route('/')
def index():
    return render_template('testsocket.html')


@app.route('/api/convert/aed-to-inr')
def aed_to_inr():
    # Fetch the live price for AED to INR,Ticker for AED to INR IS AEDINR=X
    try:
        aed_inr = stock_info.get_live_price("AEDINR=X")
        today = datetime.now().date()
        historical_data = stock_info.get_data("AEDINR=X", start_date=today, end_date=today)

        if not historical_data.empty:
            today_high = historical_data['high'].values[0]
            today_low = historical_data['low'].values[0]
        else:
            today_high = None
            today_low = None

        response = {
            "currency": "AED to INR",
            "current_rate": aed_inr,
            "today_high": today_high,
            "today_low": today_low,
            "today": today.isoformat(),
        }

        socketio.emit('currency_update', response)
        # socketio.emit('trigger_update', None)

        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/convert/usd-to-inr')
def usd_to_inr():
    # Fetch the live price for USD to INR,Ticker for USD to INR IS INR=X
    try:
        usd_inr = stock_info.get_live_price("INR=X")
        today = datetime.now().date()
        historical_data = stock_info.get_data("INR=X", start_date=today, end_date=today)

        if not historical_data.empty:
            today_high = historical_data['high'].values[0]
            today_low = historical_data['low'].values[0]
        else:
            today_high = None
            today_low = None

        response = {
            "currency": "USD to INR",
            "current_rate": usd_inr,
            "today_high": today_high,
            "today_low": today_low,
            "today": today.isoformat(),
        }
        socketio.emit('currency_update', response)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on('connect')
def handle_connect():
    global connected_clients
    connected_clients += 1
    socketio.sleep(0.1)
    print(f"Client connected. Total clients: {connected_clients}")

    socketio.emit('welcome_message', {
        'message': 'Welcome to the currency update WebSocket!',
        'status': 'success'
    }, to=request.sid)

    if connected_clients == 1:
        socketio.start_background_task(run_currency_updates)


@socketio.on('disconnect')
def handle_disconnect():
    global connected_clients
    connected_clients -= 1
    print(f"Client disconnected. Total clients: {connected_clients}")


def run_currency_updates():
    with app.app_context():
        while connected_clients > 0:
            try:
                aed_to_inr_response = aed_to_inr()
                usd_to_inr_response = usd_to_inr()
                socketio.emit('currency_update', {
                    'aed_to_inr': aed_to_inr_response,
                    'usd_to_inr': usd_to_inr_response,
                })
            except Exception as e:
                print(f"Error in fetching currency data: {e}")

            socketio.sleep(60)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)


