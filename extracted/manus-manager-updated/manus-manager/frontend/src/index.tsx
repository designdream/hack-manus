import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import './index.css';

// Create a callback function for Google OAuth
window.handleGoogleCallback = (response) => {
  // Post message to parent window with the token
  if (window.opener) {
    window.opener.postMessage({ token: response.credential }, window.location.origin);
    window.close();
  }
};

const root = createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);
