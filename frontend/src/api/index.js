import axios from "axios";

const DEMO_WARD_COORDS = {
  "Ward 1 (Kazhakoottam)": { lat: 8.5667, lng: 76.8721 },
  "Ward 2 (Technopark)": { lat: 8.55, lng: 76.88 },
  "Ward 3 (Pattom)": { lat: 8.5241, lng: 76.9366 },
  "Ward 4 (Vanchiyoor)": { lat: 8.4875, lng: 76.9525 },
  "Ward 5 (Palayam)": { lat: 8.5005, lng: 76.9536 },
  "Ward 6 (Karamana)": { lat: 8.47, lng: 76.97 },
  "Ward 7 (Nemom)": { lat: 8.45, lng: 76.96 },
  "Ward 8 (Kovalam)": { lat: 8.3988, lng: 76.982 },
};

const DEMO_GRIEVANCES = [
  {
    id: "demo-grievance-1",
    citizen_name: "Ramesh Kumar",
    phone: "9876543210",
    ward: "Ward 1 (Kazhakoottam)",
    category: "water",
    urgency: 5,
    credibility_score: 94,
    description: "Water pipeline burst near Kazhakoottam junction causing flooding and contamination risk.",
    ai_summary: "Pipeline burst causing flooding and contaminated water supply.",
    status: "open",
    created_at: "2026-05-01T10:00:00Z",
  },
  {
    id: "demo-grievance-2",
    citizen_name: "Priya Nair",
    phone: "9876543211",
    ward: "Ward 2 (Technopark)",
    category: "road",
    urgency: 4,
    credibility_score: 91,
    description: "Massive pothole on the Technopark bypass causing repeated accidents.",
    ai_summary: "Dangerous pothole near Technopark bypass.",
    status: "breached",
    created_at: "2026-05-02T09:30:00Z",
  },
  {
    id: "demo-grievance-3",
    citizen_name: "Arun Menon",
    phone: "9876543212",
    ward: "Ward 3 (Pattom)",
    category: "electricity",
    urgency: 3,
    credibility_score: 84,
    description: "Frequent power cuts in Pattom residential area for the last week.",
    ai_summary: "Recurring electricity interruptions in Pattom.",
    status: "open",
    created_at: "2026-05-03T14:15:00Z",
  },
  {
    id: "demo-grievance-4",
    citizen_name: "Lakshmi Devi",
    phone: "9876543213",
    ward: "Ward 4 (Vanchiyoor)",
    category: "sanitation",
    urgency: 4,
    credibility_score: 89,
    description: "Garbage pile-up near the market causing foul smell and mosquito breeding.",
    ai_summary: "Garbage accumulation causing hygiene and mosquito issues.",
    status: "resolved",
    created_at: "2026-05-01T16:45:00Z",
  },
  {
    id: "demo-grievance-5",
    citizen_name: "Suresh Pillai",
    phone: "9876543214",
    ward: "Ward 5 (Palayam)",
    category: "health",
    urgency: 5,
    credibility_score: 96,
    description: "Sewage overflow near the hospital entrance affecting patients and visitors.",
    ai_summary: "Sewage overflow near hospital entrance.",
    status: "open",
    created_at: "2026-05-04T08:20:00Z",
  },
  {
    id: "demo-grievance-6",
    citizen_name: "Meera Mohan",
    phone: "9876543215",
    ward: "Ward 6 (Karamana)",
    category: "water",
    urgency: 2,
    credibility_score: 72,
    description: "Low water pressure in Karamana for three days.",
    ai_summary: "Low water pressure in Karamana.",
    status: "closed",
    created_at: "2026-04-29T11:10:00Z",
  },
  {
    id: "demo-grievance-7",
    citizen_name: "Vijay Krishnan",
    phone: "9876543216",
    ward: "Ward 7 (Nemom)",
    category: "road",
    urgency: 3,
    credibility_score: 81,
    description: "Broken road divider causing unsafe wrong-side driving.",
    ai_summary: "Broken divider creating traffic safety risk.",
    status: "open",
    created_at: "2026-05-03T18:05:00Z",
  },
  {
    id: "demo-grievance-8",
    citizen_name: "Deepa Thomas",
    phone: "9876543217",
    ward: "Ward 8 (Kovalam)",
    category: "other",
    urgency: 2,
    credibility_score: 70,
    description: "Drain blockage near Kovalam beach entry causing waterlogging.",
    ai_summary: "Drain blockage causing waterlogging near beach entry.",
    status: "reopened",
    created_at: "2026-05-02T13:50:00Z",
  },
];

const DEMO_CLUSTERS = [
  {
    id: "demo-cluster-water-1",
    category: "water",
    ward: "Ward 1 (Kazhakoottam)",
    count: 2,
    summary: "Recurring water supply and pipeline issues around Kazhakoottam.",
    member_ids: ["demo-grievance-1", "demo-grievance-6"],
    members: [DEMO_GRIEVANCES[0], DEMO_GRIEVANCES[5]],
    created_at: "2026-05-04T09:00:00Z",
  },
  {
    id: "demo-cluster-road-1",
    category: "road",
    ward: "Ward 2 (Technopark)",
    count: 2,
    summary: "Road damage and traffic safety complaints near Technopark.",
    member_ids: ["demo-grievance-2", "demo-grievance-7"],
    members: [DEMO_GRIEVANCES[1], DEMO_GRIEVANCES[6]],
    created_at: "2026-05-04T10:30:00Z",
  },
];

const DEMO_BUDGET_ENTRIES = [
  {
    id: "demo-budget-1",
    department: "Water Authority",
    amount_allocated: 250000,
    amount_spent: 182500,
    description: "Emergency pipeline repairs and tanker support.",
    auditor_flagged: false,
    created_at: "2026-05-01T09:00:00Z",
  },
  {
    id: "demo-budget-2",
    department: "Roads",
    amount_allocated: 400000,
    amount_spent: 341000,
    description: "Pothole patching and drainage repairs.",
    auditor_flagged: true,
    flag_reason: "Expenditure exceeds expected materials cost",
    flagged_at: "2026-05-05T12:00:00Z",
    created_at: "2026-05-02T11:00:00Z",
  },
  {
    id: "demo-budget-3",
    department: "Sanitation",
    amount_allocated: 180000,
    amount_spent: 92000,
    description: "Garbage lifting and anti-mosquito drive.",
    auditor_flagged: false,
    created_at: "2026-05-03T14:00:00Z",
  },
];

const DEMO_OFFICER = {
  user_id: "demo-officer",
  email: "officer@nyayasetu.local",
  full_name: "Demo Officer",
  role: "officer",
  ward: "Ward 2 (Technopark)",
  phone: "9999999999",
};

function makeDemoResponse(data) {
  return Promise.resolve({
    data: {
      success: true,
      data,
      error: null,
    },
    status: 200,
    statusText: "OK",
    headers: {},
    config: {},
  });
}

function buildDemoStats() {
  const total = DEMO_GRIEVANCES.length;
  const open = DEMO_GRIEVANCES.filter((g) => g.status === "open").length;
  const resolved = DEMO_GRIEVANCES.filter((g) => ["resolved", "closed"].includes(g.status)).length;
  const critical = DEMO_GRIEVANCES.filter((g) => g.urgency >= 4).length;
  const clusters_active = DEMO_CLUSTERS.length;
  const sla_breaches = DEMO_GRIEVANCES.filter((g) => g.status === "breached").length;

  return { total, open, resolved, critical, clusters_active, sla_breaches };
}

function buildDemoMap() {
  const byWard = DEMO_GRIEVANCES.reduce((acc, grievance) => {
    const key = grievance.ward;
    if (!acc[key]) acc[key] = { count: 0, critical_count: 0 };
    acc[key].count += 1;
    if (grievance.urgency >= 4) acc[key].critical_count += 1;
    return acc;
  }, {});

  return Object.entries(DEMO_WARD_COORDS).map(([ward, coords]) => {
    const summary = byWard[ward] || { count: 0, critical_count: 0 };
    return { ward, ...summary, ...coords };
  });
}

function buildDemoTrends() {
  const byCategory = Object.entries(
    DEMO_GRIEVANCES.reduce((acc, grievance) => {
      const category = grievance.category || "other";
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {})
  )
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  const byStatus = Object.entries(
    DEMO_GRIEVANCES.reduce((acc, grievance) => {
      const status = grievance.status || "open";
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, count]) => ({ name, count }));

  const byWard = Object.entries(
    DEMO_GRIEVANCES.reduce((acc, grievance) => {
      const ward = grievance.ward || "Unknown";
      acc[ward] = (acc[ward] || 0) + 1;
      return acc;
    }, {})
  )
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  return { by_category: byCategory, by_status: byStatus, by_ward: byWard };
}

function buildDemoPredictions() {
  return DEMO_GRIEVANCES.filter((g) => g.status === "open" || g.status === "breached").map((g) => ({
    id: g.id,
    grievance_id: g.id,
    category: g.category,
    ward: g.ward,
    trend: g.urgency >= 4 ? "rising" : "stable",
    predicted_count: 1,
    confidence: g.urgency >= 4 ? 0.82 : 0.68,
    description: g.description,
    urgency: g.urgency,
    prediction: {
      predicted_hours: g.category === "water" ? 36 : g.category === "road" ? 48 : 72,
      predicted_days: g.category === "water" ? 1.5 : g.category === "road" ? 2 : 3,
      confidence: 0.78,
      category: g.category,
    },
    risk_assessment: {
      risk_level: g.status === "breached" ? "breached" : g.urgency >= 4 ? "high" : "medium",
      risk_score: g.status === "breached" ? 1 : g.urgency >= 4 ? 0.82 : 0.55,
      hours_remaining: g.status === "breached" ? 0 : 24,
      hours_over: g.status === "breached" ? 12 : 0,
      predicted_vs_sla: "demo data",
      recommendation: "Demo fallback data used while database is unavailable.",
    },
  }));
}

function buildDemoBudgetStats() {
  const total_allocated = DEMO_BUDGET_ENTRIES.reduce((sum, entry) => sum + entry.amount_allocated, 0);
  const total_spent = DEMO_BUDGET_ENTRIES.reduce((sum, entry) => sum + entry.amount_spent, 0);
  const total_flagged = DEMO_BUDGET_ENTRIES.filter((entry) => entry.auditor_flagged).length;
  const flagged_amount = DEMO_BUDGET_ENTRIES.filter((entry) => entry.auditor_flagged).reduce((sum, entry) => sum + entry.amount_allocated, 0);

  const by_department = DEMO_BUDGET_ENTRIES.map((entry) => ({
    name: entry.department,
    allocated: entry.amount_allocated,
    spent: entry.amount_spent,
    flagged: entry.auditor_flagged ? 1 : 0,
  }));

  return { total_allocated, total_spent, total_entries: DEMO_BUDGET_ENTRIES.length, total_flagged, flagged_amount, by_department };
}

function isFallbackError(error, url = "") {
  const message = String(error?.message || error?.response?.data?.error || "");
  const fallbackable = [
    "/api/dashboard/stats",
    "/api/dashboard/clusters",
    "/api/dashboard/map",
    "/api/dashboard/brief",
    "/api/dashboard/trends",
    "/api/grievances",
    "/api/predictions",
    "/api/audit/budget",
    "/api/audit/budget/stats",
    "/api/audit/flagged",
    "/api/officer/me",
    "/api/officer/assignments",
  ];

  if (!fallbackable.some((path) => url.includes(path))) return false;

  return (
    message.includes("getaddrinfo failed") ||
    message.includes("Database not configured") ||
    message.includes("Network Error") ||
    message.includes("ENOTFOUND") ||
    message.includes("ECONNREFUSED")
  );
}

function fallbackForUrl(url) {
  if (url.includes("/api/dashboard/stats")) return buildDemoStats();
  if (url.includes("/api/dashboard/map")) return buildDemoMap();
  if (url.includes("/api/dashboard/trends")) return buildDemoTrends();
  if (url.includes("/api/dashboard/clusters")) return DEMO_CLUSTERS;
  if (url.includes("/api/dashboard/brief")) {
    return { brief: "Demo brief: active water, road, and sanitation clusters are being monitored across the city." };
  }
  if (url.includes("/api/grievances")) return DEMO_GRIEVANCES;
  if (url.includes("/api/predictions")) return buildDemoPredictions();
  if (url.includes("/api/audit/budget/stats")) return buildDemoBudgetStats();
  if (url.includes("/api/audit/budget")) return DEMO_BUDGET_ENTRIES;
  if (url.includes("/api/audit/flagged")) return DEMO_BUDGET_ENTRIES.filter((entry) => entry.auditor_flagged);
  if (url.includes("/api/officer/me")) return DEMO_OFFICER;
  if (url.includes("/api/officer/assignments")) return [];
  return null;
}

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
      const fallbackData = fallbackForUrl(response?.config?.url || "");
      const errorLike = {
        message: response.data.error || "Request failed",
        response,
        config: response.config,
      };

      if (fallbackData && isFallbackError(errorLike, response?.config?.url || "")) {
        return makeDemoResponse(fallbackData);
      }

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

    const fallbackData = fallbackForUrl(error?.config?.url || error?.response?.config?.url || "");
    if (fallbackData && isFallbackError(error, error?.config?.url || error?.response?.config?.url || "")) {
      return makeDemoResponse(fallbackData);
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
