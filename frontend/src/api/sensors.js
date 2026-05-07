import apiClient from './client';

export async function fetchSensors() {
  const { data } = await apiClient.get('/api/sensors/');
  return data;
}
