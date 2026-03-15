import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 20000,
});

// Request interceptor — attach Content-Type and Authorization headers
api.interceptors.request.use(
  (config) => {
    config.headers["Content-Type"] = "application/json";
    
    // Attach JWT token if available
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — surface server-side errors and handle auth failures
api.interceptors.response.use(
  (response) => {
    if (response.data && response.data.success === false) {
      const err = new Error(response.data.error || "Request failed");
      err.response = response;
      throw err;
    }
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized — redirect to login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("authToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

/* ────────── Grievance endpoints ────────── */

export const submitGrievance = (data) => api.post("/api/grievances", data);

export const getGrievances = (params) =>
  api.get("/api/grievances", { params });

export const getGrievance = (id) => api.get(`/api/grievances/${id}`);

export const resolveGrievance = (id) =>
  api.patch(`/api/grievances/${id}/resolve`);

export const confirmResolution = (id) =>
  api.patch(`/api/grievances/${id}/confirm`);

/* ────────── Dashboard endpoints ────────── */

export const getDashboardStats = () => api.get("/api/dashboard/stats");

export const getDashboardClusters = () => api.get("/api/dashboard/clusters");

export const getDashboardMap = () => api.get("/api/dashboard/map");

export const generateBrief = () => api.get("/api/dashboard/brief");

export const getDashboardTrends = () => api.get("/api/dashboard/trends");

/* ────────── Legal / Justice-Link endpoints ────────── */

export const getLegalCases = () => api.get("/api/legal");

export const addLegalCase = (data) => api.post("/api/legal", data);

export const checkEligibility = (id) => api.get(`/api/legal/check/${id}`);

/* ────────── Translation endpoint ────────── */

export const translateGrievance = (id) => api.get(`/api/translate/${id}`);

/* ────────── AI Identity Extraction endpoint ────────── */

export const extractIdentity = (transcript) => api.post("/api/extract-identity", { transcript });

/* ────────── Community endpoint ────────── */

export const supportGrievance = (id) => api.post(`/api/grievances/${id}/support`);

/* ────────── Officer endpoints ────────── */

export const getMyAssignments = (status = null) => {
  const params = status ? { status_filter: status } : {};
  return api.get("/api/officer/assignments", { params });
};

export const getOfficerProfile = () => api.get("/api/officer/me");

export const getOfficerStats = () => api.get("/api/officer/stats");

export const updateGrievanceStatus = (id, data) =>
  api.put(`/api/officer/grievances/${id}/status`, data);

export const assignGrievance = (id, data) =>
  api.post(`/api/officer/assignments/${id}/assign`, data);

/* ────────── Railway (RailMadad 2.0) endpoints ────────── */

export const submitRailwayGrievance = (data) => api.post("/api/railway/grievances", data);

export const getRailwayGrievances = (params) => api.get("/api/railway/grievances", { params });

export const getRailwayGrievance = (id) => api.get(`/api/railway/grievances/${id}`);

export const resolveRailwayGrievance = (id) => api.patch(`/api/railway/grievances/${id}/resolve`);

export const getRailwayDashboardStats = () => api.get("/api/railway/dashboard/stats");

export const getRailwayDashboardClusters = () => api.get("/api/railway/dashboard/clusters");

export const getRailwayDashboardTrends = () => api.get("/api/railway/dashboard/trends");

export const generateRailwayBrief = () => api.get("/api/railway/dashboard/brief");

/* ────────── Audit & Budget endpoints ────────── */

export const getBudgetEntries = (params) => api.get("/api/audit/budget", { params });

export const getBudgetStats = () => api.get("/api/audit/budget/stats");

export const getFlaggedEntries = () => api.get("/api/audit/flagged");

export const createBudgetEntry = (data) => api.post("/api/audit/budget", data);

export const flagBudgetEntry = (id, reason) => api.patch(`/api/audit/budget/${id}/flag`, null, { params: { reason } });

/* ────────── Predictions endpoints ────────── */

export const getPredictions = (params) => api.get("/api/predictions", { params });

export const runPredictions = () => api.post("/api/predictions/run");

/* ────────── Email & Export endpoints ────────── */

export const sendOfficerEmail = (data) => api.post("/api/officer/send-email", data);

export const exportToExcel = (params) => {
  return api.get("/api/export/excel", {
    params,
    responseType: "blob"
  });
};

export const exportToDoc = (params) => {
  return api.get("/api/export/doc", {
    params,
    responseType: "blob"
  });
};

export default api;
