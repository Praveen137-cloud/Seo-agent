import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const startAudit = async (url, maxPages = 50) => {
  const response = await api.post('/api/audit', { url, max_pages: maxPages });
  return response.data;
};

export const getAuditStatus = async (auditId) => {
  const response = await api.get(`/api/audit/${auditId}`);
  return response.data;
};

export const getAuditIssues = async (auditId, severity = null, category = null) => {
  const params = {};
  if (severity) params.severity = severity;
  if (category) params.category = category;
  const response = await api.get(`/api/audit/${auditId}/issues`, { params });
  return response.data;
};

export const getAuditRecommendations = async (auditId) => {
  const response = await api.get(`/api/audit/${auditId}/recommendations`);
  return response.data;
};

export const getRecentAudits = async (limit = 10) => {
  const response = await api.get('/api/audits', { params: { limit } });
  return response.data;
};

export const getReportDownloadUrl = (auditId) => {
  return `${API_BASE_URL}/api/audit/${auditId}/report`;
};

export default api;
