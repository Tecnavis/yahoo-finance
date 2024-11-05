from flask import Flask, jsonify
from yahoo_fin import stock_info
from datetime import datetime

app = Flask(__name__)


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

        return jsonify({
            "currency": "AED to INR",
            "current_rate": aed_inr,
            "today_high": today_high,
            "today_low": today_low,
            "today": today,
        })
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

        return jsonify({
            "currency": "USD to INR",
            "current_rate": usd_inr,
            "today_high": today_high,
            "today_low": today_low,
            "today": today,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
