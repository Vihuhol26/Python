from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/rate")
def get_rate():
    currency = request.args.get("currency", "").upper()

    rates = {
        "USD": 100.0,
        "EUR": 110.0
    }

    if currency not in rates:
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400

    try:
        return jsonify({"rate": rates[currency]})
    except Exception:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500

if __name__ == "__main__":
    app.run()
