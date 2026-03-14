import React, { useState, useEffect, useCallback } from 'react'
import {
  getDashboardStats,
  getDashboardMap,
  getDashboardClusters,
  getGrievances,
  resolveGrievance,
  generateBrief,
} from '../api'
import StatCard from '../components/StatCard'
import GrievanceTable from '../components/GrievanceTable'
import ClusterCard from '../components/ClusterCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorCard from '../components/ErrorCard'
import Toast from '../components/Toast'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'

const TABS = ['Dashboard', 'Complaints', 'Clusters', 'Generate Brief']

export default function OfficerDashboard() {
  const [activeTab, setActiveTab] = useState('Dashboard')
  const [toast, setToast] = useState(null)

  // Dashboard tab state
  const [stats, setStats] = useState(null)
  const [mapData, setMapData] = useState([])
  const [statsLoading, setStatsLoading] = useState(true)
  const [statsError, setStatsError] = useState(null)

  // Complaints tab state
  const [grievances, setGrievances] = useState([])
  const [grievancesLoading, setGrievancesLoading] = useState(false)
  const [grievancesError, setGrievancesError] = useState(null)

  // Clusters tab state
  const [clusters, setClusters] = useState([])
  const [clustersLoading, setClustersLoading] = useState(false)
  const [clustersError, setClustersError] = useState(null)

  // Brief tab state
  const [brief, setBrief] = useState('')
  const [briefLoading, setBriefLoading] = useState(false)
  const [briefError, setBriefError] = useState(null)

  // Fetch dashboard stats + map data
  const fetchDashboard = useCallback(async () => {
    setStatsLoading(true)
    setStatsError(null)
    try {
      const [statsRes, mapRes] = await Promise.all([
        getDashboardStats(),
        getDashboardMap(),
      ])
      setStats(statsRes?.data?.data || statsRes?.data || null)
      setMapData(mapRes?.data?.data || mapRes?.data || [])
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

  // Load data on tab change
  useEffect(() => {
    try {
      if (activeTab === 'Dashboard') fetchDashboard()
      else if (activeTab === 'Complaints') fetchGrievances()
      else if (activeTab === 'Clusters') fetchClusters()
    } catch (err) {
      console.error('Tab load error:', err)
    }
  }, [activeTab, fetchDashboard, fetchGrievances, fetchClusters])

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
            <div className="mb-6 flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-navy">Complaints</h1>
              <button
                onClick={fetchGrievances}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium font-body text-gray-700 hover:bg-gray-200 transition-colors"
              >
                Refresh
              </button>
            </div>

            {grievancesError && (
              <ErrorCard message={grievancesError} onRetry={fetchGrievances} />
            )}

            <GrievanceTable
              grievances={grievances}
              onResolve={handleResolve}
              loading={grievancesLoading}
            />
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
