from flask import Flask, jsonify, render_template
from yahoo_fin import stock_info
from datetime import datetime
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')


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
    print("Client connected")
    socketio.sleep(0.1)
    emit('message', {'data': 'Connected to the server'})


@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")


@socketio.on('start_updates')
def start_currency_updates():
    """Emit currency updates to clients every 1 minute."""
    while True:
        aed_to_inr_response = aed_to_inr()
        usd_to_inr_response = usd_to_inr()
        print(f"USD to INR Response: {usd_to_inr_response}")
        print(f"AED to INR Response: {aed_to_inr_response}")
        socketio.emit('currency_update', aed_to_inr_response)
        socketio.emit('currency_update', usd_to_inr_response)
        socketio.sleep(30)


if __name__ == '__main__':
    socketio.start_background_task(start_currency_updates)
    socketio.run(app, debug=True)
