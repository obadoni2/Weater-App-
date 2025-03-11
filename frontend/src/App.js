import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [location, setLocation] = useState('');
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchWeather = async () => {
    if (!location) {
      setError('Please enter a location.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      // Fetch current weather data from the Flask backend
      const resCurrent = await fetch(`http://localhost:5000/weather/current?location=${encodeURIComponent(location)}`);
      if (!resCurrent.ok) {
        throw new Error('Failed to fetch current weather.');
      }
      const dataCurrent = await resCurrent.json();
      setCurrentWeather(dataCurrent);

      // Fetch 5-day forecast data from the Flask backend
      const resForecast = await fetch(`http://localhost:5000/weather/forecast?location=${encodeURIComponent(location)}`);
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

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchWeather();
  };

  return (
    <div className="app-container">
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

      <main className="container py-5">
        {loading && (
          <div className="loader-container">
            <div className="loader"></div>
          </div>
        )}
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
        {forecast && !loading && (
          <div className="forecast-section">
            <h2 className="text-center text-white mb-4">5-Day Forecast</h2>
            <div className="row">
              {forecast.list
                .filter((item, index) => index % 8 === 0)
                .map((item, index) => (
                  <div key={index} className="col-md-2 col-sm-4 col-6">
                    <div className="forecast-card card mb-3">
                      <div className="card-body text-center">
                        <h5>{new Date(item.dt_txt).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</h5>
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
      <footer className="text-center py-3">
        <p className="mb-0">Weather Wonder © {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
