import React, { useState, useEffect, useCallback } from 'react'
import { getGrievances, supportGrievance } from '../api'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import UrgencyBadge from '../components/UrgencyBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorCard from '../components/ErrorCard'
import Toast from '../components/Toast'

const WARD_COORDS = {
  'Ward 1 (Kazhakoottam)': [8.5667, 76.8721],
  'Ward 2 (Technopark)': [8.5500, 76.8800],
  'Ward 3 (Pattom)': [8.5241, 76.9366],
  'Ward 4 (Vanchiyoor)': [8.4875, 76.9525],
  'Ward 5 (Palayam)': [8.5005, 76.9536],
  'Ward 6 (Karamana)': [8.4700, 76.9700],
  'Ward 7 (Nemom)': [8.4500, 76.9600],
  'Ward 8 (Kovalam)': [8.3988, 76.9820],
}

const STATUS_COLORS = {
  open: '#3B82F6',
  resolved: '#10B981',
  breached: '#EF4444',
  reopened: '#F59E0B',
  closed: '#6B7280',
}

export default function CommunityFeed() {
  const [grievances, setGrievances] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)
  const [supporting, setSupporting] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getGrievances({ limit: 100 })
      setGrievances(res?.data?.data || res?.data || [])
    } catch (err) {
      setError(err?.message || 'Failed to load complaints')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleSupport = async (id) => {
    setSupporting(id)
    try {
      const res = await supportGrievance(id)
      const newCount = res?.data?.data?.support_count ?? res?.data?.support_count
      setGrievances(prev =>
        prev.map(g => g.id === id ? { ...g, support_count: newCount ?? (g.support_count || 0) + 1 } : g)
      )
      setToast({ message: 'Your support has been recorded!', type: 'success' })
    } catch (err) {
      setToast({ message: err?.message || 'Could not register support', type: 'error' })
    } finally {
      setSupporting(null)
    }
  }

  const getCoords = (ward) => {
    return WARD_COORDS[ward] || [8.505, 76.95]
  }

  // Sort by support_count descending
  const sorted = [...grievances].sort((a, b) => (b.support_count || 0) - (a.support_count || 0))

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-navy">Community Feed</h1>
        <p className="mt-1 font-body text-sm text-gray-500">
          See complaints in your area. Support issues that affect you too.
        </p>
      </div>

      {error && <ErrorCard message={error} onRetry={fetchData} />}

      {loading ? (
        <LoadingSpinner message="Loading community complaints..." />
      ) : (
        <div className="grid gap-6 lg:grid-cols-5">
          {/* Map */}
          <div className="lg:col-span-3">
            <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
              <div className="h-[500px]">
                {(() => {
                  try {
                    return (
                      <MapContainer center={[8.505, 76.95]} zoom={12} className="h-full w-full" scrollWheelZoom>
                        <TileLayer
                          attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a>'
                          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        {grievances.map((g, idx) => {
                          const coords = getCoords(g?.ward)
                          const jitter = [(Math.random() - 0.5) * 0.01, (Math.random() - 0.5) * 0.01]
                          return (
                            <CircleMarker
                              key={g?.id || idx}
                              center={[coords[0] + jitter[0], coords[1] + jitter[1]]}
                              radius={6}
                              fillColor={STATUS_COLORS[g?.status] || '#3B82F6'}
                              color="#fff"
                              weight={1}
                              fillOpacity={0.8}
                            >
                              <Popup>
                                <div className="font-body text-xs">
                                  <p className="font-bold text-navy">{g?.category || 'General'}</p>
                                  <p className="text-gray-600">{g?.ai_summary || g?.description?.slice(0, 80) || '--'}</p>
                                  <p className="mt-1 text-gray-400">{g?.ward}</p>
                                  <p className="font-semibold text-accent">{g?.support_count || 0} supporters</p>
                                </div>
                              </Popup>
                            </CircleMarker>
                          )
                        })}
                      </MapContainer>
                    )
                  } catch {
                    return <div className="flex h-full items-center justify-center text-gray-400 text-sm">Map failed to load</div>
                  }
                })()}
              </div>
            </div>

            {/* Legend */}
            <div className="mt-3 flex flex-wrap gap-3 text-xs font-body text-gray-500">
              {Object.entries(STATUS_COLORS).map(([status, color]) => (
                <span key={status} className="flex items-center gap-1">
                  <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
                  {status}
                </span>
              ))}
            </div>
          </div>

          {/* Sidebar list */}
          <div className="lg:col-span-2">
            <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
              <div className="border-b border-gray-100 px-4 py-3">
                <h2 className="font-heading text-sm font-semibold text-navy">
                  Top Issues ({sorted.length})
                </h2>
              </div>
              <div className="max-h-[500px] overflow-y-auto divide-y divide-gray-100">
                {sorted.length === 0 ? (
                  <div className="px-4 py-8 text-center text-sm text-gray-400 font-body">No complaints yet</div>
                ) : (
                  sorted.map((g, idx) => (
                    <div key={g?.id || idx} className="px-4 py-3 hover:bg-gray-50 transition-colors">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <UrgencyBadge level={g?.urgency} />
                            <span className="inline-block rounded-full bg-navy/10 px-2 py-0.5 text-[10px] font-semibold text-navy">
                              {g?.category || 'other'}
                            </span>
                          </div>
                          <p className="text-sm font-body text-gray-700 line-clamp-2">
                            {g?.ai_summary || g?.description?.slice(0, 100) || '--'}
                          </p>
                          <p className="mt-1 text-xs text-gray-400 font-body">{g?.ward}</p>
                        </div>
                        <button
                          onClick={() => handleSupport(g?.id)}
                          disabled={supporting === g?.id}
                          className="flex shrink-0 flex-col items-center gap-0.5 rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs font-medium text-gray-600 transition-colors hover:border-accent hover:text-accent focus:outline-none disabled:opacity-50"
                        >
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
                          </svg>
                          <span>{g?.support_count || 0}</span>
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
