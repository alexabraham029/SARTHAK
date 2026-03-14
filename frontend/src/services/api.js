import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Generate session ID
export const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// Legal Chat API
export const sendChatMessage = async (sessionId, message) => {
  const response = await api.post('/api/chat/', {
    session_id: sessionId,
    message: message,
    include_history: true,
  });
  return response.data;
};

// Semantic Search API
export const searchLaws = async (query, lawFilter = null, topK = 5) => {
  const response = await api.post('/api/search/', {
    query: query,
    law_filter: lawFilter,
    top_k: topK,
  });
  return response.data;
};

// Case Summarizer API
export const summarizeCase = async (sessionId, caseQuery) => {
  const response = await api.post('/api/cases/summarize', {
    session_id: sessionId,
    case_query: caseQuery,
  });
  return response.data;
};

// Case Similarity API
export const findSimilarCases = async (caseDescription, courtFilter = null, topK = 5) => {
  const response = await api.post('/api/cases/similar', {
    case_description: caseDescription,
    court_filter: courtFilter,
    top_k: topK,
  });
  return response.data;
};

// Document Upload API
export const uploadDocument = async (sessionId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(`/api/documents/upload?session_id=${sessionId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Document Query API
export const queryDocument = async (sessionId, documentId, query) => {
  const response = await api.post('/api/documents/query', {
    session_id: sessionId,
    document_id: documentId,
    query: query,
  });
  return response.data;
};

// Get available laws
export const getAvailableLaws = async () => {
  const response = await api.get('/api/search/laws');
  return response.data;
};

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
