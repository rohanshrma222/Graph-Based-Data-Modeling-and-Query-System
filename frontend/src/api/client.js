import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api';

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
  const { data } = await axios.get('http://localhost:8000/health', { timeout: 10000 });
  return data;
};

export default api;
