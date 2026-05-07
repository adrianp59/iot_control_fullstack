import { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { fetchReadings, fetchHumidityReadings } from '../api/readings';

export default function SensorCard({ sensor, since }) {
  const [tempReadings, setTempReadings] = useState([]);
  const [humidityReadings, setHumidityReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    Promise.all([
      fetchReadings(sensor.deviceId, since),
      fetchHumidityReadings(sensor.deviceId, since),
    ])
      .then(([temps, humidities]) => {
        setTempReadings(temps);
        setHumidityReadings(humidities);
      })
      .catch(() => setError('Failed to load readings.'))
      .finally(() => setLoading(false));
  }, [sensor.deviceId, since]);

  const latestTemp = tempReadings.length > 0 ? tempReadings[tempReadings.length - 1].value : null;
  const tempValues = tempReadings.map((r) => r.value);
  const minTemp = tempValues.length > 0 ? Math.min(...tempValues) : null;
  const maxTemp = tempValues.length > 0 ? Math.max(...tempValues) : null;

  const latestHumidity = humidityReadings.length > 0 ? humidityReadings[humidityReadings.length - 1].value : null;
  const humidityValues = humidityReadings.map((r) => r.value);
  const minHumidity = humidityValues.length > 0 ? Math.min(...humidityValues) : null;
  const maxHumidity = humidityValues.length > 0 ? Math.max(...humidityValues) : null;

  return (
    <div className="sensor-card">
      <div className="sensor-card-header">
        <div>
          <h2 className="sensor-name">{sensor.name || sensor.deviceId}</h2>
          {sensor.location && (
            <span className="sensor-location">{sensor.location}</span>
          )}
        </div>
        <span className="sensor-device-id">{sensor.deviceId}</span>
      </div>

      <div className="sensor-stats">
        <Stat label="Temp" value={latestTemp} unit="°C" />
        <Stat label="Min" value={minTemp} unit="°C" />
        <Stat label="Max" value={maxTemp} unit="°C" />
        <div className="stat">
          <span className="stat-label">Readings</span>
          <span className="stat-value plain">{tempReadings.length}</span>
        </div>
      </div>

      <div className="sensor-stats">
        <Stat label="Humidity" value={latestHumidity} unit="%" />
        <Stat label="Min" value={minHumidity} unit="%" />
        <Stat label="Max" value={maxHumidity} unit="%" />
        <div className="stat">
          <span className="stat-label">Readings</span>
          <span className="stat-value plain">{humidityReadings.length}</span>
        </div>
      </div>

      <div className="chart-area">
        {loading && <p className="chart-msg">Loading…</p>}
        {error && <p className="chart-msg error">{error}</p>}
        {!loading && !error && (
          <>
            <p className="chart-label">Temperature</p>
            {tempReadings.length === 0 ? (
              <p className="chart-msg">No temperature data for this period.</p>
            ) : (
              <ReadingChart data={tempReadings} unit="°C" color="var(--accent)" />
            )}
            <p className="chart-label">Humidity</p>
            {humidityReadings.length === 0 ? (
              <p className="chart-msg">No humidity data for this period.</p>
            ) : (
              <ReadingChart data={humidityReadings} unit="%" color="var(--accent-secondary, #38bdf8)" />
            )}
          </>
        )}
      </div>
    </div>
  );
}

function ReadingChart({ data, unit, color }) {
  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={formatTime}
          tick={{ fontSize: 11, fill: 'var(--text)' }}
          minTickGap={40}
        />
        <YAxis
          unit={unit}
          tick={{ fontSize: 11, fill: 'var(--text)' }}
          width={52}
          domain={['auto', 'auto']}
        />
        <Tooltip content={<CustomTooltip unit={unit} />} />
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function Stat({ label, value, unit }) {
  return (
    <div className="stat">
      <span className="stat-label">{label}</span>
      <span className="stat-value">
        {value !== null ? `${value.toFixed(1)}${unit}` : '—'}
      </span>
    </div>
  );
}

function CustomTooltip({ active, payload, unit }) {
  if (!active || !payload?.length) return null;
  const { timestamp, value } = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <p className="tooltip-time">{formatFullTime(timestamp)}</p>
      <p className="tooltip-value">{value.toFixed(2)}{unit}</p>
    </div>
  );
}

function formatTime(isoString) {
  const d = new Date(isoString);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatFullTime(isoString) {
  const d = new Date(isoString);
  return d.toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}
