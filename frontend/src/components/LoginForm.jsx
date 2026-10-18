import { useState } from 'react';
import { login } from '../api/auth';

export default function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const token = await login(username, password);
      onLogin(token);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrapper">
      <form className="login-card" onSubmit={handleSubmit} noValidate>
        <h1 className="login-title">IoT Dashboard</h1>
        <p className="login-subtitle">Sign in to view your sensors</p>

        {error && <p className="login-error" role="alert">{error}</p>}

        <label className="field-label" htmlFor="username">Username</label>
        <input
          id="username"
          className="field-input"
          type="text"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label className="field-label" htmlFor="password">Password</label>
        <input
          id="password"
          className="field-input"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  );
}
