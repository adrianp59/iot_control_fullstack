import apiClient from './client';

export async function fetchSensors() {
  const { data } = await apiClient.get('/api/sensors/');
  return data;
}

export async function sendACCommand(commandPayload) {
  const { data } = await apiClient.post('/api/ac-control/v2/', commandPayload);
  return data;
}
