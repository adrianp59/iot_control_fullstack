import apiClient from './client';

/**
 * @param {string} deviceId  – sensor device_id (slug)
 * @param {string|null} since – ISO 8601 datetime string; null = fetch all
 */
export async function fetchReadings(deviceId, since = null) {
  const params = {
    sensorId: deviceId,
    ordering: 'timestamp',
  };
  if (since) {
    params.since = since;
  }
  const { data } = await apiClient.get('/api/readings/', { params });
  return data;
}

export async function fetchHumidityReadings(deviceId, since = null) {
  const params = {
    sensorId: deviceId,
    ordering: 'timestamp',
  };
  if (since) {
    params.since = since;
  }
  const { data } = await apiClient.get('/api/humidity-readings/', { params });
  return data;
}
