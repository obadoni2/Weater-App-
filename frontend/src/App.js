import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  // State variables to manage location input, weather data, errors, and loading status
  const [location, setLocation] = useState('');
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // useEffect to test API connection by fetching London's current weather on mount
  useEffect(() => {
    fetch('http://localhost:5000/weather/current?location=London')
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error('Error:', error));
  }, []);

  // Function to fetch current weather and forecast data from the backend
  const fetchWeather = async (loc) => {
    if (!loc) {
      setError('Please enter a location.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      // Fetch current weather
      const resCurrent = await fetch(`http://localhost:5000/weather/current?location=${encodeURIComponent(loc)}`);
      if (!resCurrent.ok) {
        throw new Error('Failed to fetch current weather.');
      }
      const dataCurrent = await resCurrent.json();
      setCurrentWeather(dataCurrent);

      // Fetch 5-day forecast
      const resForecast = await fetch(`http://localhost:5000/weather/forecast?location=${encodeURIComponent(loc)}`);
      if (!resForecast.ok) {
        throw new Error('Failed to fetch forecast.');
      }
      const dataForecast = await resForecast.json();
      setForecast(dataForecast);
    } catch (err) {
      setError(err.message);
      setCurrentWeather(null);
      setForecast(null);
    }
    setLoading(false);
  };

  // Handle form submission to fetch weather data for the entered location
  const handleSubmit = (e) => {
    e.preventDefault();
    fetchWeather(location);
  };

  return (
    <div className="app-container">
      {/* Header with search form */}
      <header className="hero">
        <div className="hero-overlay">
          <div className="hero-content text-center">
            <h1>Weather Wonder</h1>
            <p>Discover the weather in your favorite locations</p>
            <form onSubmit={handleSubmit} className="search-form mt-4">
              <input
                type="text"
                placeholder="Enter location (city, zip, landmark...)"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
              <button type="submit">Search</button>
            </form>
            {error && <div className="alert alert-danger mt-3">{error}</div>}
          </div>
        </div>
      </header>

      {/* Main content area */}
      <main className="container py-5">
        {/* Loading indicator */}
        {loading && (
          <div className="loader-container">
            <div className="loader"></div>
          </div>
        )}

        {/* Current weather display */}
        {currentWeather && !loading && (
          <div className="current-weather card mx-auto mb-5">
            <div className="card-body text-center">
              <h2>{currentWeather.name}, {currentWeather.sys.country}</h2>
              <div className="weather-details d-flex justify-content-center align-items-center">
                <img
                  src={`http://openweathermap.org/img/wn/${currentWeather.weather[0].icon}@2x.png`}
                  alt={currentWeather.weather[0].description}
                />
                <div className="weather-info ml-3">
                  <h3>{currentWeather.main.temp} °C</h3>
                  <p className="mb-0 text-capitalize">{currentWeather.weather[0].description}</p>
                  <p className="mb-0">Humidity: {currentWeather.main.humidity}%</p>
                  <p className="mb-0">Wind: {currentWeather.wind.speed} m/s</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 5-day forecast display */}
        {forecast && !loading && (
          <div className="forecast-section">
            <h2 className="text-center text-white mb-4">5-Day Forecast</h2>
            <div className="row">
              {forecast.list
                .filter((item, index) => index % 8 === 0) // Select one entry per day (every 8th item, assuming 3-hour intervals)
                .map((item, index) => (
                  <div key={index} className="col-md-2 col-sm-4 col-6">
                    <div className="forecast-card card mb-3">
                      <div className="card-body text-center">
                        <h5>
                          {new Date(item.dt_txt).toLocaleDateString('en-US', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric',
                          })}
                        </h5>
                        <img
                          src={`http://openweathermap.org/img/wn/${item.weather[0].icon}@2x.png`}
                          alt={item.weather[0].description}
                        />
                        <p className="text-capitalize">{item.weather[0].description}</p>
                        <p>{item.main.temp} °C</p>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-3">
        <p className="mb-0">Weather Wonder © {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;