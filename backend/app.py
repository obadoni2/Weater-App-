from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import requests
import os
import json
from dateutil.parser import parse as parse_date
import logging

# Initialize Flask app
app = Flask(__name__, static_folder='build', static_url_path='')

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for cross-origin requests from frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Load OpenWeatherMap API key from environment variable
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
if not OPENWEATHER_API_KEY:
    raise ValueError("OpenWeatherMap API key not found. Set the OPENWEATHER_API_KEY environment variable.")

# --- Database Model ---
class WeatherQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    result = db.Column(db.Text)  # Stores weather API response as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'result': json.loads(self.result) if self.result else None,
            'created_at': self.created_at.isoformat()
        }

# --- Utility Functions ---
def parse_date(date_str):
    """Parse a date string into a date object."""
    try:
        return parse_date(date_str).date()
    except ValueError:
        raise ValueError("Dates must be in a valid format (e.g., YYYY-MM-DD).")

def fetch_current_weather(location):
    """Fetch current weather data from OpenWeatherMap."""
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise Exception("Invalid API key.")
    elif response.status_code == 404:
        raise Exception("Location not found.")
    else:
        raise Exception(f"Failed to fetch weather data: {response.status_code}")

def fetch_forecast_weather(location):
    """Fetch 5-day weather forecast from OpenWeatherMap."""
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise Exception("Invalid API key.")
    elif response.status_code == 404:
        raise Exception("Location not found.")
    else:
        raise Exception(f"Failed to fetch forecast data: {response.status_code}")

# --- API Endpoints ---

### Get Current Weather
@app.route('/weather/current', methods=['GET'])
def get_current_weather_endpoint():
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required.'}), 400
    try:
        weather = fetch_current_weather(location)
        return jsonify(weather)
    except Exception as e:
        app.logger.error(f"Error fetching current weather: {str(e)}")
        return jsonify({'error': str(e)}), 400 if "Location" in str(e) else 500

### Get 5-Day Forecast
@app.route('/weather/forecast', methods=['GET'])
def get_forecast():
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required.'}), 400
    try:
        forecast = fetch_forecast_weather(location)
        return jsonify(forecast)
    except Exception as e:
        app.logger.error(f"Error fetching forecast: {str(e)}")
        return jsonify({'error': str(e)}), 400 if "Location" in str(e) else 500

# --- CRUD Endpoints for Weather Queries ---

### CREATE: Add a New Weather Query
@app.route('/queries', methods=['POST'])
def create_query():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided.'}), 400

    location = data.get('location')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not all([location, start_date_str, end_date_str]):
        return jsonify({'error': 'Location, start_date, and end_date are required.'}), 400

    try:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        if start_date > end_date:
            return jsonify({'error': 'start_date cannot be after end_date.'}), 400

        weather_data = fetch_current_weather(location)
        query_record = WeatherQuery(
            location=location,
            start_date=start_date,
            end_date=end_date,
            result=json.dumps(weather_data)
        )
        db.session.add(query_record)
        db.session.commit()
        return jsonify(query_record.as_dict()), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating query: {str(e)}")
        return jsonify({'error': str(e)}), 400 if "Location" in str(e) else 500

### READ: Get All Weather Queries
@app.route('/queries', methods=['GET'])
def get_queries():
    try:
        queries = WeatherQuery.query.all()
        return jsonify([q.as_dict() for q in queries]), 200
    except Exception as e:
        app.logger.error(f"Error fetching queries: {str(e)}")
        return jsonify({'error': 'Failed to fetch queries.'}), 500

### READ: Get a Specific Weather Query by ID
@app.route('/queries/<int:query_id>', methods=['GET'])
def get_query(query_id):
    try:
        query_record = WeatherQuery.query.get(query_id)
        if not query_record:
            return jsonify({'error': 'Query not found.'}), 404
        return jsonify(query_record.as_dict()), 200
    except Exception as e:
        app.logger.error(f"Error fetching query {query_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch query.'}), 500

### UPDATE: Modify an Existing Weather Query
@app.route('/queries/<int:query_id>', methods=['PUT'])
def update_query(query_id):
    query_record = WeatherQuery.query.get(query_id)
    if not query_record:
        return jsonify({'error': 'Query not found.'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided.'}), 400

    try:
        if 'location' in data:
            weather_data = fetch_current_weather(data['location'])
            query_record.location = data['location']
            query_record.result = json.dumps(weather_data)
        if 'start_date' in data:
            query_record.start_date = parse_date(data['start_date'])
        if 'end_date' in data:
            query_record.end_date = parse_date(data['end_date'])

        if query_record.start_date > query_record.end_date:
            return jsonify({'error': 'start_date cannot be after end_date.'}), 400

        db.session.commit()
        return jsonify(query_record.as_dict()), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating query {query_id}: {str(e)}")
        return jsonify({'error': str(e)}), 400 if "Location" in str(e) or "Dates" in str(e) else 500

### DELETE: Remove a Weather Query
@app.route('/queries/<int:query_id>', methods=['DELETE'])
def delete_query(query_id):
    query_record = WeatherQuery.query.get(query_id)
    if not query_record:
        return jsonify({'error': 'Query not found.'}), 404

    try:
        db.session.delete(query_record)
        db.session.commit()
        return jsonify({'message': 'Query deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting query {query_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete query.'}), 500

### EXPORT: Export All Queries as JSON
@app.route('/queries/export', methods=['GET'])
def export_queries():
    try:
        queries = WeatherQuery.query.all()
        data = [q.as_dict() for q in queries]
        return jsonify(data), 200
    except Exception as e:
        app.logger.error(f"Error exporting queries: {str(e)}")
        return jsonify({'error': 'Failed to export queries.'}), 500

# --- Serve React Frontend ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve the React frontend from the 'build' directory."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# --- Initialize Database and Run App ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)