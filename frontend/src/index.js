import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.js';
import './App.css';
// Create a React root and render the App component within React.StrictMode
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
