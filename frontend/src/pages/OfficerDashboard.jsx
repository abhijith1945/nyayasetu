import React, { useState, useEffect, useCallback } from 'react'
import {
  getDashboardStats,
  getDashboardMap,
  getDashboardClusters,
  getDashboardTrends,
  getGrievances,
  resolveGrievance,
  generateBrief,
  getBudgetEntries,
  getBudgetStats,
  createBudgetEntry,
  getPredictions,
  runPredictions,
  sendOfficerEmail,
  exportToExcel,
  exportToDoc,
} from '../api'
import StatCard from '../components/StatCard'
import GrievanceTable from '../components/GrievanceTable'
import ClusterCard from '../components/ClusterCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorCard from '../components/ErrorCard'
import Toast from '../components/Toast'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const TABS = ['Dashboard', 'Complaints', 'Clusters', 'Predictions', 'Audit & Budget', 'Generate Brief']
const PIE_COLORS = ['#3B82F6', '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', '#6B7280']

export default function OfficerDashboard() {
  const [activeTab, setActiveTab] = useState('Dashboard')
  const [toast, setToast] = useState(null)

  // Dashboard tab state
  const [stats, setStats] = useState(null)
  const [mapData, setMapData] = useState([])
  const [trends, setTrends] = useState(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [statsError, setStatsError] = useState(null)

  // Complaints tab state
  const [grievances, setGrievances] = useState([])
  const [grievancesLoading, setGrievancesLoading] = useState(false)
  const [grievancesError, setGrievancesError] = useState(null)

  // Email modal state
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [emailForm, setEmailForm] = useState({ recipient_email: '', subject: '', message: '', grievance_id: '' })
  const [emailLoading, setEmailLoading] = useState(false)

  // Export state
  const [exportLoading, setExportLoading] = useState(false)

  // Clusters tab state
  const [clusters, setClusters] = useState([])
  const [clustersLoading, setClustersLoading] = useState(false)
  const [clustersError, setClustersError] = useState(null)

  // Brief tab state
  const [brief, setBrief] = useState('')
  const [briefLoading, setBriefLoading] = useState(false)
  const [briefError, setBriefError] = useState(null)

  // Audit & Budget tab state
  const [budgetEntries, setBudgetEntries] = useState([])
  const [budgetStats, setBudgetStats] = useState(null)
  const [auditLoading, setAuditLoading] = useState(false)
  const [auditError, setAuditError] = useState(null)
  const [showBudgetForm, setShowBudgetForm] = useState(false)
  const [budgetForm, setBudgetForm] = useState({ department: '', amount_allocated: '', description: '', grievance_id: '' })

  // Predictions tab state
  const [predictions, setPredictions] = useState([])
  const [predictionsLoading, setPredictionsLoading] = useState(false)
  const [predictionsError, setPredictionsError] = useState(null)

  // Fetch dashboard stats + map data
  const fetchDashboard = useCallback(async () => {
    setStatsLoading(true)
    setStatsError(null)
    try {
      const [statsRes, mapRes, trendsRes] = await Promise.all([
        getDashboardStats(),
        getDashboardMap(),
        getDashboardTrends(),
      ])
      setStats(statsRes?.data?.data || statsRes?.data || null)
      setMapData(mapRes?.data?.data || mapRes?.data || [])
      setTrends(trendsRes?.data?.data || trendsRes?.data || null)
    } catch (err) {
      console.error('Dashboard fetch error:', err)
      setStatsError(err?.message || 'Failed to load dashboard')
    } finally {
      setStatsLoading(false)
    }
  }, [])

  // Fetch grievances
  const fetchGrievances = useCallback(async () => {
    setGrievancesLoading(true)
    setGrievancesError(null)
    try {
      const res = await getGrievances({ limit: 100 })
      setGrievances(res?.data?.data || res?.data || [])
    } catch (err) {
      console.error('Grievances fetch error:', err)
      setGrievancesError(err?.message || 'Failed to load complaints')
    } finally {
      setGrievancesLoading(false)
    }
  }, [])

  // Fetch clusters
  const fetchClusters = useCallback(async () => {
    setClustersLoading(true)
    setClustersError(null)
    try {
      const res = await getDashboardClusters()
      setClusters(res?.data?.data || res?.data || [])
    } catch (err) {
      console.error('Clusters fetch error:', err)
      setClustersError(err?.message || 'Failed to load clusters')
    } finally {
      setClustersLoading(false)
    }
  }, [])

  // Fetch audit data
  const fetchAudit = useCallback(async () => {
    setAuditLoading(true)
    setAuditError(null)
    try {
      const [entriesRes, statsRes] = await Promise.all([
        getBudgetEntries({}),
        getBudgetStats(),
      ])
      setBudgetEntries(entriesRes?.data?.data || entriesRes?.data || [])
      setBudgetStats(statsRes?.data?.data || statsRes?.data || null)
    } catch (err) {
      setAuditError(err?.message || 'Failed to load audit data')
    } finally {
      setAuditLoading(false)
    }
  }, [])

  // Fetch predictions
  const fetchPredictions = useCallback(async () => {
    setPredictionsLoading(true)
    setPredictionsError(null)
    try {
      const res = await getPredictions({})
      setPredictions(res?.data?.data || res?.data || [])
    } catch (err) {
      setPredictionsError(err?.message || 'Failed to load predictions')
    } finally {
      setPredictionsLoading(false)
    }
  }, [])

  // Load data on tab change
  useEffect(() => {
    try {
      if (activeTab === 'Dashboard') fetchDashboard()
      else if (activeTab === 'Complaints') fetchGrievances()
      else if (activeTab === 'Clusters') fetchClusters()
      else if (activeTab === 'Audit & Budget') fetchAudit()
      else if (activeTab === 'Predictions') fetchPredictions()
    } catch (err) {
      console.error('Tab load error:', err)
    }
  }, [activeTab, fetchDashboard, fetchGrievances, fetchClusters, fetchAudit, fetchPredictions])

  // Handle resolve
  const handleResolve = async (id) => {
    try {
      const res = await resolveGrievance(id)
      const msg = res?.data?.data?.message || res?.data?.message || 'Grievance resolved'
      setToast({ message: msg, type: 'success' })
      fetchGrievances()
      fetchDashboard()
    } catch (err) {
      console.error('Resolve error:', err)
      setToast({ message: err?.message || 'Failed to resolve', type: 'error' })
    }
  }

  // Generate brief
  const handleGenerateBrief = async () => {
    setBriefLoading(true)
    setBriefError(null)
    try {
      const res = await generateBrief()
      setBrief(res?.data?.data?.brief || res?.data?.brief || 'No brief generated.')
    } catch (err) {
      console.error('Brief generation error:', err)
      setBriefError(err?.message || 'Failed to generate brief')
    } finally {
      setBriefLoading(false)
    }
  }

  // Handle budget form submission
  const handleBudgetSubmit = async (e) => {
    e.preventDefault()
    try {
      await createBudgetEntry({
        department: budgetForm.department,
        amount_allocated: parseFloat(budgetForm.amount_allocated),
        description: budgetForm.description || null,
        grievance_id: budgetForm.grievance_id || null,
      })
      setToast({ message: 'Budget entry created', type: 'success' })
      setBudgetForm({ department: '', amount_allocated: '', description: '', grievance_id: '' })
      setShowBudgetForm(false)
      fetchAudit()
    } catch (err) {
      setToast({ message: err?.message || 'Failed to create budget entry', type: 'error' })
    }
  }

  // Handle run predictions
  const handleRunPredictions = async () => {
    setPredictionsLoading(true)
    try {
      await runPredictions()
      setToast({ message: 'Predictions generated', type: 'success' })
      fetchPredictions()
    } catch (err) {
      setToast({ message: err?.message || 'Failed to run predictions', type: 'error' })
      setPredictionsLoading(false)
    }
  }

  // Handle send email
  const handleSendEmail = async (e) => {
    e.preventDefault()
    setEmailLoading(true)
    try {
      await sendOfficerEmail({
        recipient_email: emailForm.recipient_email,
        subject: emailForm.subject,
        message: emailForm.message,
        grievance_id: emailForm.grievance_id || null,
      })
      setToast({ message: 'Email sent successfully!', type: 'success' })
      setEmailForm({ recipient_email: '', subject: '', message: '', grievance_id: '' })
      setShowEmailModal(false)
    } catch (err) {
      console.error('Email error:', err)
      setToast({ message: err?.message || 'Failed to send email', type: 'error' })
    } finally {
      setEmailLoading(false)
    }
  }

  // Handle export to Excel
  const handleExportExcel = async () => {
    setExportLoading(true)
    try {
      const response = await exportToExcel({})
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `grievances_export_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      setToast({ message: 'Excel file downloaded', type: 'success' })
    } catch (err) {
      console.error('Excel export error:', err)
      setToast({ message: err?.message || 'Failed to export to Excel', type: 'error' })
    } finally {
      setExportLoading(false)
    }
  }

  // Handle export to Doc
  const handleExportDoc = async () => {
    setExportLoading(true)
    try {
      const response = await exportToDoc({})
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `grievances_report_${new Date().toISOString().split('T')[0]}.docx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      setToast({ message: 'Word document downloaded', type: 'success' })
    } catch (err) {
      console.error('Doc export error:', err)
      setToast({ message: err?.message || 'Failed to export to Doc', type: 'error' })
    } finally {
      setExportLoading(false)
    }
  }

  // Map marker color based on count
  const getMarkerColor = (count) => {
    if (count >= 16) return '#EF4444'
    if (count >= 6) return '#F59E0B'
    return '#10B981'
  }

  return (
    <div className="flex min-h-[calc(100vh-64px)]">
      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
      )}

      {/* Sidebar */}
      <aside className="hidden w-56 shrink-0 border-r border-gray-200 bg-white lg:block">
        <div className="p-4">
          <h2 className="mb-4 font-heading text-lg font-bold text-navy">Officer Panel</h2>
          <nav className="space-y-1">
            {TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`w-full rounded-lg px-3 py-2 text-left text-sm font-medium font-body transition-colors ${
                  activeTab === tab
                    ? 'bg-accent/10 text-accent'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-navy'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
      </aside>

      {/* Mobile tab bar */}
      <div className="fixed bottom-0 left-0 right-0 z-40 flex border-t border-gray-200 bg-white lg:hidden">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-3 text-xs font-bold font-body transition-colors ${
              activeTab === tab ? 'text-accent bg-accent/5' : 'text-gray-500'
            }`}
          >
            {tab.split(' ')[0]}
          </button>
        ))}
      </div>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-4 pb-20 sm:p-6 lg:p-8 lg:pb-8">
        {/* ─── DASHBOARD TAB ─── */}
        {activeTab === 'Dashboard' && (
          <div>
            <h1 className="mb-6 font-heading text-2xl font-bold text-navy">Dashboard</h1>

            {statsError && <ErrorCard message={statsError} onRetry={fetchDashboard} />}

            {statsLoading ? (
              <LoadingSpinner message="Loading dashboard..." />
            ) : (
              <>
                {/* Stat cards */}
                <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
                  <StatCard title="Total Complaints" value={stats?.total ?? 0} color="border-navy" icon="📋" />
                  <StatCard title="Open" value={stats?.open ?? 0} color="border-blue-500" icon="📂" />
                  <StatCard title="Critical" value={stats?.critical ?? 0} color="border-critical" icon="🚨" />
                  <StatCard title="Active Clusters" value={stats?.clusters_active ?? 0} color="border-accent" icon="🔗" />
                </div>

                {/* Charts */}
                {trends && (
                  <div className="mb-8 grid gap-4 lg:grid-cols-2">
                    {/* Category Bar Chart */}
                    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                      <h3 className="mb-3 font-heading text-sm font-semibold text-navy">Complaints by Category</h3>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={trends.by_category || []}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                          <YAxis allowDecimals={false} />
                          <Tooltip />
                          <Bar dataKey="count" fill="#10B981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Status Pie Chart */}
                    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                      <h3 className="mb-3 font-heading text-sm font-semibold text-navy">Status Distribution</h3>
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={trends.by_status || []}
                            dataKey="count"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={90}
                            label={({ name, count }) => `${name} (${count})`}
                          >
                            {(trends.by_status || []).map((_, i) => (
                              <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Map */}
                <div className="mb-8 overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
                  <h2 className="border-b border-gray-100 px-5 py-3 font-heading text-base font-semibold text-navy">
                    Ward Complaint Map
                  </h2>
                  <div className="h-[400px]">
                    {(() => {
                      try {
                        return (
                          <MapContainer
                            center={[8.505, 76.95]}
                            zoom={12}
                            className="h-full w-full"
                            scrollWheelZoom={true}
                          >
                            <TileLayer
                              attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a>'
                              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />
                            {Array.isArray(mapData) && mapData.map((point, idx) => (
                              <CircleMarker
                                key={point?.ward || idx}
                                center={[point?.lat || 8.5, point?.lng || 76.95]}
                                radius={Math.max(8, Math.min(25, (point?.count || 0) * 2))}
                                fillColor={getMarkerColor(point?.count || 0)}
                                color="#fff"
                                weight={2}
                                opacity={1}
                                fillOpacity={0.7}
                              >
                                <Popup>
                                  <div className="font-body text-sm">
                                    <p className="font-bold">{point?.ward || 'Unknown'}</p>
                                    <p>Complaints: {point?.count ?? 0}</p>
                                    <p>Critical: {point?.critical_count ?? 0}</p>
                                  </div>
                                </Popup>
                              </CircleMarker>
                            ))}
                          </MapContainer>
                        )
                      } catch (mapErr) {
                        console.error('Map render error:', mapErr)
                        return (
                          <div className="flex h-full items-center justify-center text-gray-400 text-sm">
                            Map failed to load
                          </div>
                        )
                      }
                    })()}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* ─── COMPLAINTS TAB ─── */}
        {activeTab === 'Complaints' && (
          <div>
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <h1 className="font-heading text-2xl font-bold text-navy">Complaints</h1>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={fetchGrievances}
                  className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium font-body text-gray-700 hover:bg-gray-200 transition-colors"
                >
                  Refresh
                </button>
                <button
                  onClick={handleExportExcel}
                  disabled={exportLoading}
                  className="rounded-lg bg-green-100 px-4 py-2 text-sm font-medium font-body text-green-700 hover:bg-green-200 transition-colors disabled:opacity-50"
                >
                  📊 Excel
                </button>
                <button
                  onClick={handleExportDoc}
                  disabled={exportLoading}
                  className="rounded-lg bg-blue-100 px-4 py-2 text-sm font-medium font-body text-blue-700 hover:bg-blue-200 transition-colors disabled:opacity-50"
                >
                  📄 Word
                </button>
                <button
                  onClick={() => setShowEmailModal(true)}
                  className="rounded-lg bg-accent/10 px-4 py-2 text-sm font-medium font-body text-accent hover:bg-accent/20 transition-colors"
                >
                  ✉️ Email
                </button>
              </div>
            </div>

            {grievancesError && (
              <ErrorCard message={grievancesError} onRetry={fetchGrievances} />
            )}

            <GrievanceTable
              grievances={grievances}
              onResolve={handleResolve}
              loading={grievancesLoading}
            />

            {/* Email Modal */}
            {showEmailModal && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
                  <div className="mb-4 flex items-center justify-between">
                    <h2 className="font-heading text-lg font-bold text-navy">Send Email</h2>
                    <button
                      onClick={() => setShowEmailModal(false)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      ✕
                    </button>
                  </div>

                  <form onSubmit={handleSendEmail} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 font-body">
                        Recipient Email <span className="text-critical">*</span>
                      </label>
                      <input
                        type="email"
                        required
                        value={emailForm.recipient_email}
                        onChange={(e) => setEmailForm({ ...emailForm, recipient_email: e.target.value })}
                        className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-body text-sm focus:border-accent focus:outline-none"
                        placeholder="citizen@example.com"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 font-body">
                        Subject <span className="text-critical">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={emailForm.subject}
                        onChange={(e) => setEmailForm({ ...emailForm, subject: e.target.value })}
                        className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-body text-sm focus:border-accent focus:outline-none"
                        placeholder="Grievance Status Update"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 font-body">
                        Message <span className="text-critical">*</span>
                      </label>
                      <textarea
                        required
                        value={emailForm.message}
                        onChange={(e) => setEmailForm({ ...emailForm, message: e.target.value })}
                        rows="5"
                        className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-body text-sm focus:border-accent focus:outline-none"
                        placeholder="Write your message here..."
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 font-body">
                        Grievance ID (optional)
                      </label>
                      <input
                        type="text"
                        value={emailForm.grievance_id}
                        onChange={(e) => setEmailForm({ ...emailForm, grievance_id: e.target.value })}
                        className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-body text-sm focus:border-accent focus:outline-none"
                        placeholder="Leave blank if not related to specific grievance"
                      />
                    </div>

                    <div className="flex gap-2 pt-4">
                      <button
                        type="button"
                        onClick={() => setShowEmailModal(false)}
                        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium font-body text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={emailLoading}
                        className="flex-1 rounded-lg bg-accent px-4 py-2 text-sm font-medium font-body text-white hover:bg-accent/90 transition-colors disabled:opacity-50"
                      >
                        {emailLoading ? 'Sending...' : 'Send Email'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ─── CLUSTERS TAB ─── */}
        {activeTab === 'Clusters' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-navy">Complaint Clusters</h1>
              <button
                onClick={fetchClusters}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium font-body text-gray-700 hover:bg-gray-200 transition-colors"
              >
                Refresh
              </button>
            </div>

            {clustersError && (
              <ErrorCard message={clustersError} onRetry={fetchClusters} />
            )}

            {clustersLoading ? (
              <LoadingSpinner message="Loading clusters..." />
            ) : clusters.length === 0 ? (
              <div className="rounded-lg border border-gray-200 bg-white p-12 text-center text-gray-400 font-body">
                No active clusters yet. Clusters are detected automatically every 10 minutes.
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {clusters.map((cluster, idx) => (
                  <ClusterCard key={cluster?.id || idx} cluster={cluster} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ─── PREDICTIONS TAB ─── */}
        {activeTab === 'Predictions' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-navy">Predictive Resource Allocation</h1>
              <div className="flex gap-2">
                <button
                  onClick={handleRunPredictions}
                  disabled={predictionsLoading}
                  className="rounded-lg bg-accent px-4 py-2 text-sm font-medium font-body text-white hover:bg-accent/90 transition-colors disabled:opacity-50"
                >
                  {predictionsLoading ? 'Generating...' : 'Run Predictions'}
                </button>
                <button
                  onClick={fetchPredictions}
                  className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium font-body text-gray-700 hover:bg-gray-200 transition-colors"
                >
                  Refresh
                </button>
              </div>
            </div>

            {predictionsError && <ErrorCard message={predictionsError} onRetry={fetchPredictions} />}

            {predictionsLoading ? (
              <LoadingSpinner message="Analysing historical patterns..." />
            ) : predictions.length === 0 ? (
              <div className="rounded-lg border border-gray-200 bg-white p-12 text-center text-gray-400 font-body">
                <p className="mb-4">No predictions yet. Click "Run Predictions" to analyse historical data.</p>
                <p className="text-xs">Requires at least 3 months of complaint data per ward/category.</p>
              </div>
            ) : (
              <>
                {/* Prediction Cards */}
                <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {predictions.map((p, idx) => (
                    <div key={p?.id || idx} className={`rounded-lg border bg-white p-4 shadow-sm ${
                      p.predicted_count >= 10 ? 'border-red-300' : p.predicted_count >= 5 ? 'border-yellow-300' : 'border-gray-200'
                    }`}>
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-heading text-sm font-semibold text-navy">{p.ward}</p>
                          <p className="text-xs text-gray-500 font-body">{p.category} | {p.month}</p>
                        </div>
                        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
                          p.trend === 'rising' ? 'bg-red-100 text-red-700' :
                          p.trend === 'falling' ? 'bg-green-100 text-green-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {p.trend === 'rising' ? '↑' : p.trend === 'falling' ? '↓' : '→'} {p.trend}
                        </span>
                      </div>
                      <div className="mt-3">
                        <p className="text-2xl font-bold text-navy">{p.predicted_count}</p>
                        <p className="text-xs text-gray-400 font-body">predicted complaints</p>
                      </div>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="flex-1 rounded-full bg-gray-200 h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${
                              p.confidence >= 0.8 ? 'bg-green-500' : p.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${(p.confidence || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500 font-body">{Math.round((p.confidence || 0) * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Predictions Bar Chart */}
                <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                  <h3 className="mb-3 font-heading text-sm font-semibold text-navy">Predicted Complaints by Ward</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={
                      // Aggregate predictions by ward
                      Object.entries(
                        predictions.reduce((acc, p) => {
                          acc[p.ward] = (acc[p.ward] || 0) + p.predicted_count
                          return acc
                        }, {})
                      ).map(([ward, count]) => ({ name: ward, predicted: count }))
                    }>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="predicted" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </>
            )}
          </div>
        )}

        {/* ─── AUDIT & BUDGET TAB ─── */}
        {activeTab === 'Audit & Budget' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-navy">Audit & Budget Tracking</h1>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowBudgetForm(!showBudgetForm)}
                  className="rounded-lg bg-accent px-4 py-2 text-sm font-medium font-body text-white hover:bg-accent/90 transition-colors"
                >
                  {showBudgetForm ? 'Cancel' : 'Allocate Budget'}
                </button>
                <button
                  onClick={fetchAudit}
                  className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium font-body text-gray-700 hover:bg-gray-200 transition-colors"
                >
                  Refresh
                </button>
              </div>
            </div>

            {auditError && <ErrorCard message={auditError} onRetry={fetchAudit} />}

            {/* Budget Form */}
            {showBudgetForm && (
              <form onSubmit={handleBudgetSubmit} className="mb-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                <h3 className="mb-3 font-heading text-sm font-semibold text-navy">New Budget Allocation</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    type="text"
                    placeholder="Department"
                    value={budgetForm.department}
                    onChange={(e) => setBudgetForm(f => ({ ...f, department: e.target.value }))}
                    className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-body"
                    required
                  />
                  <input
                    type="number"
                    placeholder="Amount (INR)"
                    value={budgetForm.amount_allocated}
                    onChange={(e) => setBudgetForm(f => ({ ...f, amount_allocated: e.target.value }))}
                    className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-body"
                    required
                    min="0"
                    step="0.01"
                  />
                  <input
                    type="text"
                    placeholder="Grievance ID (optional)"
                    value={budgetForm.grievance_id}
                    onChange={(e) => setBudgetForm(f => ({ ...f, grievance_id: e.target.value }))}
                    className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-body"
                  />
                  <input
                    type="text"
                    placeholder="Description"
                    value={budgetForm.description}
                    onChange={(e) => setBudgetForm(f => ({ ...f, description: e.target.value }))}
                    className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-body"
                  />
                </div>
                <button
                  type="submit"
                  className="mt-3 rounded-lg bg-navy px-4 py-2 text-sm font-medium text-white hover:bg-navy/90"
                >
                  Create Entry
                </button>
              </form>
            )}

            {auditLoading ? (
              <LoadingSpinner message="Loading audit data..." />
            ) : (
              <>
                {/* Budget Stats */}
                {budgetStats && (
                  <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
                    <StatCard title="Total Allocated" value={`₹${(budgetStats.total_allocated || 0).toLocaleString()}`} color="border-blue-500" icon="💰" />
                    <StatCard title="Total Spent" value={`₹${(budgetStats.total_spent || 0).toLocaleString()}`} color="border-green-500" icon="📊" />
                    <StatCard title="Flagged Entries" value={budgetStats.total_flagged || 0} color="border-critical" icon="🚩" />
                    <StatCard title="Flagged Amount" value={`₹${(budgetStats.flagged_amount || 0).toLocaleString()}`} color="border-red-500" icon="⚠️" />
                  </div>
                )}

                {/* Flagged Entries Alert */}
                {budgetEntries.filter(e => e.auditor_flagged).length > 0 && (
                  <div className="mb-6 rounded-lg border-2 border-red-300 bg-red-50 p-4">
                    <h3 className="font-heading text-sm font-semibold text-red-800 mb-2">Embezzlement Risk Alerts</h3>
                    {budgetEntries.filter(e => e.auditor_flagged).map((entry, idx) => (
                      <div key={entry?.id || idx} className="mb-2 rounded bg-white p-3 border border-red-200">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="text-sm font-semibold text-red-700 font-body">{entry.department}</p>
                            <p className="text-xs text-red-600 font-body">{entry.flag_reason}</p>
                          </div>
                          <span className="text-sm font-bold text-red-700">₹{(entry.amount_allocated || 0).toLocaleString()}</span>
                        </div>
                        {entry.flagged_at && (
                          <p className="mt-1 text-xs text-gray-400 font-body">Flagged: {new Date(entry.flagged_at).toLocaleString()}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Budget Entries Table */}
                {budgetEntries.length > 0 ? (
                  <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 font-body">Department</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 font-body">Allocated</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 font-body">Spent</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 font-body">Description</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 font-body">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {budgetEntries.map((entry, idx) => (
                          <tr key={entry?.id || idx} className={entry.auditor_flagged ? 'bg-red-50' : 'hover:bg-gray-50'}>
                            <td className="px-4 py-3 text-sm font-body font-medium text-gray-900">{entry.department}</td>
                            <td className="px-4 py-3 text-sm font-body text-gray-600">₹{(entry.amount_allocated || 0).toLocaleString()}</td>
                            <td className="px-4 py-3 text-sm font-body text-gray-600">₹{(entry.amount_spent || 0).toLocaleString()}</td>
                            <td className="max-w-xs truncate px-4 py-3 text-sm font-body text-gray-600">{entry.description || '-'}</td>
                            <td className="px-4 py-3">
                              <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${
                                entry.auditor_flagged ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                              }`}>
                                {entry.auditor_flagged ? 'FLAGGED' : 'Clean'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="rounded-lg border border-gray-200 bg-white p-12 text-center text-gray-400 font-body">
                    No budget entries yet. Use "Allocate Budget" to track spending on grievance resolution.
                  </div>
                )}

                {/* Department Breakdown Chart */}
                {budgetStats?.by_department && budgetStats.by_department.length > 0 && (
                  <div className="mt-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                    <h3 className="mb-3 font-heading text-sm font-semibold text-navy">Budget by Department</h3>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={budgetStats.by_department}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                        <YAxis allowDecimals={false} />
                        <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                        <Legend />
                        <Bar dataKey="allocated" fill="#3B82F6" name="Allocated" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="spent" fill="#10B981" name="Spent" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ─── GENERATE BRIEF TAB ─── */}
        {activeTab === 'Generate Brief' && (
          <div className="print-full">
            <h1 className="mb-6 font-heading text-2xl font-bold text-navy no-print">
              Governance Intelligence Brief
            </h1>

            {!brief && !briefLoading && !briefError && (
              <div className="text-center py-12">
                <button
                  onClick={handleGenerateBrief}
                  disabled={briefLoading}
                  className="rounded-lg bg-accent px-8 py-3 text-base font-semibold text-white shadow-sm transition-all hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 disabled:opacity-50"
                >
                  Generate Governance Intelligence Brief
                </button>
                <p className="mt-3 text-sm text-gray-400 font-body">
                  AI will analyse all active clusters and generate a comprehensive report
                </p>
              </div>
            )}

            {briefLoading && (
              <LoadingSpinner message="AI is analysing patterns..." />
            )}

            {briefError && (
              <ErrorCard message={briefError} onRetry={handleGenerateBrief} />
            )}

            {brief && !briefLoading && (
              <div>
                <div className="no-print mb-4 flex gap-3">
                  <button
                    onClick={handleGenerateBrief}
                    className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium font-body text-gray-700 hover:bg-gray-200 transition-colors"
                  >
                    Regenerate
                  </button>
                  <button
                    onClick={() => window.print()}
                    className="rounded-lg bg-navy px-4 py-2 text-sm font-medium font-body text-white hover:bg-navy/90 transition-colors"
                  >
                    Export as PDF
                  </button>
                </div>

                <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm prose prose-sm max-w-none font-body">
                  {brief.split('\n').map((line, i) => {
                    if (!line.trim()) return <br key={i} />
                    if (line.startsWith('# '))
                      return <h1 key={i} className="font-heading text-xl font-bold text-navy mt-4 mb-2">{line.slice(2)}</h1>
                    if (line.startsWith('## '))
                      return <h2 key={i} className="font-heading text-lg font-semibold text-navy mt-4 mb-2">{line.slice(3)}</h2>
                    if (line.startsWith('### '))
                      return <h3 key={i} className="font-heading text-base font-semibold text-navy mt-3 mb-1">{line.slice(4)}</h3>
                    if (line.startsWith('- '))
                      return <li key={i} className="ml-4 text-gray-700">{line.slice(2)}</li>
                    if (line.startsWith('**') && line.endsWith('**'))
                      return <p key={i} className="font-bold text-gray-800">{line.slice(2, -2)}</p>
                    return <p key={i} className="text-gray-700 leading-relaxed">{line}</p>
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
