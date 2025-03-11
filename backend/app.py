from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
import json

app = Flask(__name__, static_folder='build', static_url_path='')

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set your OpenWeatherMap API key.
# Replace 'eEmma1111' with your actual key or set an environment variable named OPENWEATHER_API_KEY.
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'eEmma1111')

# --- Database Model ---
class WeatherQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    result = db.Column(db.Text)  # Stores the weather API response as a JSON string
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
    """Parses a date string (YYYY-MM-DD) and returns a date object or None if invalid."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def fetch_current_weather(location):
    """Fetches current weather data from OpenWeatherMap using a location query."""
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_forecast_weather(location):
    """Fetches a 5-day weather forecast from OpenWeatherMap using a location query."""
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# --- API Endpoints ---

# Get current weather based on a provided location (e.g., city, zip)
@app.route('/weather/current', methods=['GET'])
def get_current_weather_endpoint():
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required.'}), 400
    
    weather = fetch_current_weather(location)
    if weather:
        return jsonify(weather)
    return jsonify({'error': 'Could not fetch weather data. Check the location or try again later.'}), 404

# Get a 5-day forecast based on a provided location
@app.route('/weather/forecast', methods=['GET'])
def get_forecast():
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required.'}), 400
    
    forecast = fetch_forecast_weather(location)
    if forecast:
        return jsonify(forecast)
    return jsonify({'error': 'Could not fetch forecast data. Check the location or try again later.'}), 404

# --- CRUD Endpoints for Weather Queries ---

# CREATE: Add a new weather query record
@app.route('/queries', methods=['POST'])
def create_query():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided.'}), 400

    location = data.get('location')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    
    if not location or not start_date_str or not end_date_str:
        return jsonify({'error': 'Location, start_date, and end_date are required.'}), 400
    
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)
    if not start_date or not end_date:
        return jsonify({'error': 'Dates must be in YYYY-MM-DD format.'}), 400
    
    if start_date > end_date:
        return jsonify({'error': 'start_date cannot be after end_date.'}), 400

    # Validate location by fetching current weather data
    weather_data = fetch_current_weather(location)
    if not weather_data:
        return jsonify({'error': 'Invalid location or unable to fetch weather data for the provided location.'}), 400

    query_record = WeatherQuery(
        location=location,
        start_date=start_date,
        end_date=end_date,
        result=json.dumps(weather_data)
    )
    db.session.add(query_record)
    db.session.commit()
    
    return jsonify(query_record.as_dict()), 201

# READ: Get all weather query records
@app.route('/queries', methods=['GET'])
def get_queries():
    queries = WeatherQuery.query.all()
    return jsonify([q.as_dict() for q in queries]), 200

# READ: Get a specific weather query record by ID
@app.route('/queries/<int:query_id>', methods=['GET'])
def get_query(query_id):
    query_record = WeatherQuery.query.get(query_id)
    if not query_record:
        return jsonify({'error': 'Query not found.'}), 404
    return jsonify(query_record.as_dict()), 200

# UPDATE: Modify an existing weather query record by ID
@app.route('/queries/<int:query_id>', methods=['PUT'])
def update_query(query_id):
    query_record = WeatherQuery.query.get(query_id)
    if not query_record:
        return jsonify({'error': 'Query not found.'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided.'}), 400

    location = data.get('location')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if location:
        weather_data = fetch_current_weather(location)
        if not weather_data:
            return jsonify({'error': 'Invalid location or unable to fetch weather data for the provided location.'}), 400
        query_record.location = location
        query_record.result = json.dumps(weather_data)

    if start_date_str:
        new_start_date = parse_date(start_date_str)
        if not new_start_date:
            return jsonify({'error': 'start_date must be in YYYY-MM-DD format.'}), 400
        query_record.start_date = new_start_date

    if end_date_str:
        new_end_date = parse_date(end_date_str)
        if not new_end_date:
            return jsonify({'error': 'end_date must be in YYYY-MM-DD format.'}), 400
        query_record.end_date = new_end_date

    if query_record.start_date > query_record.end_date:
        return jsonify({'error': 'start_date cannot be after end_date.'}), 400

    db.session.commit()
    return jsonify(query_record.as_dict()), 200

# DELETE: Remove a weather query record by ID
@app.route('/queries/<int:query_id>', methods=['DELETE'])
def delete_query(query_id):
    query_record = WeatherQuery.query.get(query_id)
    if not query_record:
        return jsonify({'error': 'Query not found.'}), 404

    db.session.delete(query_record)
    db.session.commit()
    return jsonify({'message': 'Query deleted successfully.'}), 200

# Optional: Export all queries as JSON
@app.route('/queries/export', methods=['GET'])
def export_queries():
    queries = WeatherQuery.query.all()
    data = [q.as_dict() for q in queries]
    return jsonify(data), 200

# --- Serve React Frontend ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# --- Initialize Database ---
@app.before_first_request
def create_tables():
    db.create_all()

# --- Run the Application ---
if __name__ == '__main__':
    app.run(debug=True)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    