import { useState, useEffect } from 'react';
import { refresh } from './api/auth';
import { setLogoutCallback } from './api/client';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import './App.css';

export default function App() {
  const [accessToken, setAccessToken] = useState(null);
  const [bootstrapping, setBootstrapping] = useState(true);

  // Register a logout callback so the axios interceptor can clear auth state
  useEffect(() => {
    setLogoutCallback(() => setAccessToken(null));
  }, []);

  // Silently restore session on mount via the HttpOnly refresh cookie
  useEffect(() => {
    refresh()
      .then(setAccessToken)
      .catch(() => {}) // no cookie → show login
      .finally(() => setBootstrapping(false));
  }, []);

  if (bootstrapping) {
    return <div className="boot-screen">Loading…</div>;
  }

  if (!accessToken) {
    return <LoginForm onLogin={setAccessToken} />;
  }

  return <Dashboard onLogout={() => setAccessToken(null)} />;
}

