import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 20000,
});

// Request interceptor — attach Content-Type header
api.interceptors.request.use(
  (config) => {
    config.headers["Content-Type"] = "application/json";
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — surface server-side errors
api.interceptors.response.use(
  (response) => {
    if (response.data && response.data.success === false) {
      const err = new Error(response.data.error || "Request failed");
      err.response = response;
      throw err;
    }
    return response;
  },
  (error) => Promise.reject(error)
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

/* ────────── Legal / Justice-Link endpoints ────────── */

export const getLegalCases = () => api.get("/api/legal");

export const addLegalCase = (data) => api.post("/api/legal", data);

export const checkEligibility = (id) => api.get(`/api/legal/check/${id}`);

/* ────────── Translation endpoint ────────── */

export const translateGrievance = (id) => api.get(`/api/translate/${id}`);

export default api;
