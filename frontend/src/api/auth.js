import axios from 'axios';
import apiClient, { setToken, clearToken } from './client';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function login(username, password) {
  const { data } = await axios.post(
    `${BASE_URL}/api/token/`,
    { username, password },
    { withCredentials: true }
  );
  setToken(data.access);
  return data.access;
}

export async function refresh() {
  const { data } = await axios.post(
    `${BASE_URL}/api/token/refresh/`,
    {},
    { withCredentials: true }
  );
  setToken(data.access);
  return data.access;
}

export async function logout() {
  try {
    await apiClient.post('/api/token/blacklist/');
  } catch {
    // ignore errors — cookie will expire anyway
  } finally {
    clearToken();
  }
}
