import axios from 'axios';

const DEFAULT_API_BASE = 'https://graph-based-data-modeling-and-query-6272.onrender.com';
const API_BASE = (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE).replace(/\/$/, '');
const BASE_URL = `${API_BASE}/api`;

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

export const fetchGraph = async () => {
  const { data } = await api.get('/graph');
  return data;
};

export const fetchNode = async (nodeId) => {
  const { data } = await api.get(`/graph/node/${encodeURIComponent(nodeId)}`);
  return data;
};

export const fetchSubgraph = async (nodeIds) => {
  const ids = Array.isArray(nodeIds) ? nodeIds.join(',') : nodeIds;
  const { data } = await api.get('/graph/subgraph', {
    params: { node_ids: ids },
  });
  return data;
};

export const sendQuery = async (question, conversationHistory = []) => {
  const { data } = await api.post('/query', {
    question,
    conversation_history: conversationHistory,
  });
  return data;
};

export const fetchHealth = async () => {
  const { data } = await axios.get(`${API_BASE}/health`, { timeout: 10000 });
  return data;
};

export default api;
