import { useEffect, useState, useCallback } from 'react';
import { fetchSensors } from '../api/sensors';
import { logout } from '../api/auth';
import { clearToken } from '../api/client';
import TimeRangeSelector from './TimeRangeSelector';
import SensorCard from './SensorCard';

export default function Dashboard({ onLogout }) {
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [rangeLabel, setRangeLabel] = useState('6h');
  const [since, setSince] = useState(() => sinceFromHours(6));

  useEffect(() => {
    fetchSensors()
      .then(setSensors)
      .catch(() => setError('Failed to load sensors.'))
      .finally(() => setLoading(false));
  }, []);

  const handleRangeChange = useCallback((label, hours) => {
    setRangeLabel(label);
    setSince(sinceFromHours(hours));
  }, []);

  async function handleLogout() {
    await logout();
    clearToken();
    onLogout();
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="dashboard-title">
          <span className="dashboard-title-icon">🌡</span>
          <h1>IoT Sensor Dashboard</h1>
        </div>
        <button className="btn-logout" onClick={handleLogout}>Sign out</button>
      </header>

      <div className="dashboard-toolbar">
        <TimeRangeSelector value={rangeLabel} onChange={handleRangeChange} />
      </div>

      {loading && <p className="dashboard-status">Loading sensors…</p>}
      {error && <p className="dashboard-status error">{error}</p>}

      {!loading && !error && sensors.length === 0 && (
        <p className="dashboard-status">No sensors found.</p>
      )}

      <div className="sensor-grid">
        {sensors.map((sensor) => (
          <SensorCard key={sensor.deviceId} sensor={sensor} since={since} />
        ))}
      </div>
    </div>
  );
}

function sinceFromHours(hours) {
  if (!hours) return null;
  const d = new Date();
  d.setHours(d.getHours() - hours);
  return d.toISOString();
}
