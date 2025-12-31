import traceback

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
from optimizer import VacationOptimizer
from typing import cast, Literal

import holidays


_strategy_options = Literal["spread", "continuous"]


app = Flask(
    __name__,
    static_folder='../frontend/static',
    template_folder='../frontend/templates'
    )
CORS(app)

cache = Cache(app, config={"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 86400})


@app.route("/")
def index():
    """Basic info endpoint"""
    return render_template("index.html")


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('../frontend/static', path)


@app.route("/api/optimize", methods=["GET", "POST"])
@cache.cached(timeout=86400, query_string=True)
def optimize_vacation():
    """
    Optimizes vacation day placement.

    Query params (GET) or JSON body (POST)
    - year: int
    - days: int
    - country: str (ISO Country Code, default 'PR')
    - blackout_dates: list of date strings (optional)
    - strategy: type of strategy to be used (go for continuous block or spread around the year)

    Returns:
        JSON with optimized vacation schedule
    """
    try:
        if request.method == "POST":
            data = request.json or {}
            year = int(data.get("year", 2026))
            vacation_days = int(data.get("days", 15))
            country = data.get("country", "PR")
            blackout_dates = data.get("blackout_dates", [])
            custom_holidays = data.get("custom_holidays", [])
            exclude_holidays = data.get("exclude_holidays", [])
        else:
            year = int(request.args.get("year", 2025))
            vacation_days = int(request.args.get("days", 15))
            country = request.args.get("country", "US")
            blackout_dates = []
            custom_holidays = []
            exclude_holidays = []

        if not 2020 <= year <= 2030:
            return jsonify({"error": "Year must be between 2020 and 2030"}), 400
        if not 1 <= vacation_days <= 50:
            return jsonify({"error": "Vacation days must be between 1 and 50"}), 400

        optimizer = VacationOptimizer(
            year, vacation_days, country, blackout_dates, custom_holidays, exclude_holidays
        )
        result = optimizer.optimize()

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        error_details = traceback.format_exc()
        app.logger.error(f"Optimization error: {error_details}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/get_holidays', methods=['POST'])
def get_holidays():
    try:
        data = request.json
        year = int(data.get('year', 0))
        country = data.get('country', 'PR')
        holidays_obj = holidays.country_holidays(country=country, years=year)
        holiday_strs = {date.strftime("%Y-%m-%d"): name for date, name in holidays_obj.items()}
        print(holiday_strs)
        return jsonify(holiday_strs), 200
    except ValueError as e:
        return jsonify({"error": f"Invalid input {str(e)}"}), 400
    except Exception as e:
        error_details = traceback.format_exc()
        app.logger.error(f"Error getting holidays: {error_details}")
        return jsonify({"error: Internal Server Error"}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error", "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
