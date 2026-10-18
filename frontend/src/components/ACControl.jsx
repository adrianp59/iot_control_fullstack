import { useState } from 'react';
import { sendACCommand } from '../api/sensors';

const MODE_OPTIONS = [
  { value: 'off', label: 'Off' },
  { value: 'cool', label: 'Cool' },
  { value: 'heat', label: 'Heat' },
  { value: 'auto', label: 'Auto' },
  { value: 'dry', label: 'Dry' },
];

const FAN_OPTIONS = [
  { value: 'eco', label: 'Eco' },
  { value: 'high', label: 'High' },
];

const MODE_TEMP_RANGES = {
  cool: { min: 18, max: 25, defaultValue: 22 },
  heat: { min: 20, max: 30, defaultValue: 24 },
  auto: { min: 18, max: 30, defaultValue: 24 },
  dry: { min: 18, max: 30, defaultValue: 24 },
};

const FAN_MODES = new Set(['cool', 'heat', 'dry']);

export default function ACControl({ sensors }) {
  const [selectedDevice, setSelectedDevice] = useState('');
  const [selectedMode, setSelectedMode] = useState('off');
  const [selectedTemp, setSelectedTemp] = useState(24);
  const [selectedFan, setSelectedFan] = useState('eco');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleDeviceChange(e) {
    setSelectedDevice(e.target.value);
    setStatus(null);
  }

  function handleModeSelect(mode) {
    setSelectedMode(mode);
    setStatus(null);

    if (mode === 'off') {
      return;
    }

    const range = MODE_TEMP_RANGES[mode];
    setSelectedTemp((current) => {
      if (current < range.min) return range.min;
      if (current > range.max) return range.max;
      return current;
    });
  }

  function handleTempChange(e) {
    setSelectedTemp(Number(e.target.value));
    setStatus(null);
  }

  function handleFanSelect(fan) {
    setSelectedFan(fan);
    setStatus(null);
  }

  const tempRange = selectedMode === 'off' ? null : MODE_TEMP_RANGES[selectedMode];
  const fanAvailable = FAN_MODES.has(selectedMode);
  const canSend = selectedDevice && (selectedMode === 'off' || (selectedTemp && (!fanAvailable || selectedFan)));

  async function handleSend() {
    if (!canSend) return;

    const payload = {
      deviceId: selectedDevice,
      power: selectedMode === 'off' ? 0 : 1,
    };

    if (selectedMode !== 'off') {
      payload.mode = selectedMode;
      payload.temp = selectedTemp;
      if (fanAvailable) {
        payload.fan = selectedFan;
      }
    }

    setLoading(true);
    setStatus(null);

    try {
      const data = await sendACCommand(payload);
      setStatus({ type: 'success', message: data.message || 'Command sent successfully.' });
    } catch (err) {
      const errData = err.response?.data;
      const message =
        errData?.message ||
        formatErrors(errData?.errors) ||
        'Failed to send command.';
      setStatus({ type: 'error', message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ac-control">
      <div className="ac-control-card">
        <div className="ac-section">
          <label className="ac-control-label" htmlFor="ac-device-select">
            Device
          </label>
          <select
            id="ac-device-select"
            className="ac-select"
            value={selectedDevice}
            onChange={handleDeviceChange}
          >
            <option value="">Select a device…</option>
            {sensors.map((sensor) => (
              <option key={sensor.deviceId} value={sensor.deviceId}>
                {sensor.name || sensor.deviceId}
                {sensor.location ? ` — ${sensor.location}` : ''}
              </option>
            ))}
          </select>
        </div>

        <div className="ac-section">
          <span className="ac-control-label">Mode</span>
          <div className="ac-commands">
            {MODE_OPTIONS.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                className={`command-btn${selectedMode === value ? ' active' : ''}`}
                onClick={() => handleModeSelect(value)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {tempRange && (
          <div className="ac-section">
            <label className="ac-control-label" htmlFor="ac-temp-slider">
              Temperature
            </label>
            <div className="ac-slider-row">
              <input
                id="ac-temp-slider"
                className="ac-temp-slider"
                type="range"
                min={tempRange.min}
                max={tempRange.max}
                value={selectedTemp}
                onChange={handleTempChange}
              />
              <span className="ac-temp-badge">{selectedTemp}°C</span>
            </div>
            <p className="ac-hint">Available range: {tempRange.min}°C to {tempRange.max}°C</p>
          </div>
        )}

        {fanAvailable && (
          <div className="ac-section">
            <span className="ac-control-label">Fan speed</span>
            <div className="ac-commands">
              {FAN_OPTIONS.map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  className={`command-btn${selectedFan === value ? ' active' : ''}`}
                  onClick={() => handleFanSelect(value)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}

        {selectedMode === 'auto' && (
          <p className="ac-hint">Fan speed is managed automatically in auto mode.</p>
        )}

        <button
          className="btn-primary"
          onClick={handleSend}
          disabled={!canSend || loading}
        >
          {loading ? 'Sending…' : 'Send Command'}
        </button>

        {status && (
          <p className={`ac-status${status.type === 'error' ? ' error' : ''}`}>
            {status.message}
          </p>
        )}
      </div>
    </div>
  );
}

function formatErrors(errors) {
  if (!errors) return null;
  if (typeof errors === 'string') return errors;
  if (Array.isArray(errors)) return errors.join(' ');
  if (typeof errors !== 'object') return null;

  return Object.entries(errors)
    .map(([field, message]) => {
      if (Array.isArray(message)) {
        return `${field}: ${message.join(', ')}`;
      }
      return `${field}: ${message}`;
    })
    .join(' | ');
}
