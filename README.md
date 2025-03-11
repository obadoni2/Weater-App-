
# Weather Apph

## Overview
I built this Weather App to showcase my skills in developing a full-stack web application. The app provides real-time weather information using the OpenWeatherMap API. The backend is built with Python Flask and SQLAlchemy (using SQLite for data persistence), and it also integrates a React-based frontend that is served as static files by Flask. With this project, I demonstrate my abilities in API integration, CRUD operations, and deploying a cohesive application.

## Features
- Real-Time Weather Data: Fetches current weather and a 5-day forecast based on user-supplied locations (for example, city or zip code).
- CRUD Operations: Allows creation, reading, updating, and deletion of weather query records stored in an SQLite database.
- API Integration: Leverages the OpenWeatherMap API to obtain live weather data.
- Integrated Frontend: A React-built frontend offers a modern and responsive user interface.
- Data Persistence: Uses SQLAlchemy with SQLite to persist user queries and API responses.

## Tech Stack
- Backend: Python, Flask, Flask-SQLAlchemy, Requests
- Database: SQLite (managed via SQLAlchemy)
- Weather API: OpenWeatherMap API
- Frontend: React (built and served as static files)

## Getting Started

### Prerequisites
Before getting started, make sure you have the following installed:
- Python 3.x
- Node.js and npm
- Git (optional, for cloning the repository)

### Installation

1. Clone the Repository:
   ```bash
   git clone https://github.com/yourusername/weather-app.git
   cd weather-app/backend
   ```

2. Set Up a Virtual Environment:
   I created and activated a virtual environment:
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install Python Dependencies:
   I installed the required packages using:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Environment Variables:
   I set my OpenWeatherMap API key as an environment variable:
   ```bash
   # On Windows:
   set OPENWEATHER_API_KEY=your_openweather_api_key

   # On macOS/Linux:
   export OPENWEATHER_API_KEY=your_openweather_api_key
   ```
   Alternatively, you can replace the placeholder in the code with your actual API key (though using environment variables is more secure).

5. Build and Integrate the Frontend (Optional):
   If you wish to use the React frontend:
   - Navigate to the frontend directory:
     ```bash
     cd ../frontend
     npm install
     npm run build
     ```
   - Then, copy or move the generated build folder into the backend directory so Flask can serve it:
     ```bash
     move build ..\backend\
     ```

## Running the Application

1. Start the Flask Backend:
   From the backend directory, I ran:
   ```bash
   python app.py
   ```
2. Access the Application:
   Open your browser and go to http://localhost:5000. If the React frontend is integrated, you will see the UI; otherwise, you can test the API endpoints directly.

## API Endpoints

Below are the key API endpoints I implemented:

- GET /weather/current?location=<location>
  Retrieves current weather data for the specified location.

- GET /weather/forecast?location=<location>
  Retrieves a 5-day weather forecast for the specified location.

- CRUD Endpoints for Weather Queries:
  - POST /queries: Create a new weather query record.
    Payload: JSON with location, start_date (YYYY-MM-DD), and end_date (YYYY-MM-DD).
  - GET /queries: Retrieve all weather query records.
  - GET /queries/<id>: Retrieve a specific weather query record by ID.
  - PUT /queries/<id>: Update an existing weather query record.
  - DELETE /queries/<id>: Delete a weather query record.
  - GET /queries/export: Export all weather query records as JSON.

## Database
I used SQLite as the database for this project. The database file (weather.db) is created automatically in the backend directory when the app is run for the first time.

## Contributing
I welcome contributions to improve this project. If you'd like to contribute, follow these steps:
1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Make your changes and commit them (git commit -m "Describe your changes").
4. Push to the branch (git push origin feature-branch).
5. Open a pull request.

## License
This project is licensed under the MIT License.

## Contact
For any questions or feedback, feel free to reach out:
- Email: obadoniemma@gmail.com
- GitHub: https://github.com/obadoni2
```

You can adjust any sections (such as the repository URL, contact details, or any additional information) to reflect your project specifics and personal style. Enjoy your Weather App project!
