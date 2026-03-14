import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getGrievance, confirmResolution } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorCard from '../components/ErrorCard'
import UrgencyBadge from '../components/UrgencyBadge'
import Toast from '../components/Toast'

const STATUS_COLORS = {
  open: 'bg-blue-100 text-blue-800',
  resolved: 'bg-green-100 text-green-800',
  closed: 'bg-gray-100 text-gray-800',
  breached: 'bg-red-100 text-red-800',
  reopened: 'bg-orange-100 text-orange-800',
}

const ACTION_ICONS = {
  submitted: '\u{1F4DD}',
  escalated: '\u26A0\uFE0F',
  resolved: '\u2705',
  reopened: '\u{1F504}',
  sms_sent: '\u{1F4F1}',
  breach_detected: '\u{1F6A8}',
}

export default function TrackGrievance() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [confirming, setConfirming] = useState(false)
  const [toast, setToast] = useState(null)

  const fetchData = async () => {
    setLoading(true); setError(null)
    try {
      const res = await getGrievance(id)
      setData(res?.data?.data || res?.data)
    } catch (err) {
      setError(err?.message || 'Failed to load grievance')
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchData() }, [id])

  const handleConfirm = async () => {
    setConfirming(true)
    try {
      await confirmResolution(id)
      setToast({ message: 'Resolution confirmed. Thank you!', type: 'success' })
      fetchData()
    } catch (err) {
      setToast({ message: err?.message || 'Confirmation failed', type: 'error' })
    } finally { setConfirming(false) }
  }

  if (loading) return <LoadingSpinner message="Loading grievance details..." />
  if (error) return <div className="max-w-2xl mx-auto px-4 py-8"><ErrorCard message={error} onRetry={fetchData} /></div>

  const grievance = data?.grievance || data || {}
  const actions = data?.actions || []
  const status = grievance?.status || 'unknown'

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <h1 className="text-2xl font-heading font-bold text-navy mb-6">Track Complaint</h1>

      <div className="bg-white rounded-xl shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-gray-500 font-mono">#{(grievance?.id || '').slice(0, 8)}</span>
          <span className={'px-3 py-1 rounded-full text-sm font-medium ' + (STATUS_COLORS[status] || 'bg-gray-100 text-gray-800')}>
            {status?.toUpperCase()}
          </span>
        </div>
        <h2 className="font-heading font-semibold text-lg mb-2">{grievance?.ai_summary || grievance?.description?.slice(0, 80) || 'No summary'}</h2>
        <p className="text-gray-600 text-sm mb-4">{grievance?.description || ''}</p>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div><span className="text-gray-400">Name:</span> <span className="font-medium">{grievance?.citizen_name || '-'}</span></div>
          <div><span className="text-gray-400">Ward:</span> <span className="font-medium">{grievance?.ward || '-'}</span></div>
          <div><span className="text-gray-400">Category:</span> <span className="font-medium capitalize">{grievance?.category || '-'}</span></div>
          <div><span className="text-gray-400">Urgency:</span> <UrgencyBadge level={grievance?.urgency} /></div>
          <div className="col-span-2"><span className="text-gray-400">Hash:</span> <span className="font-mono text-xs break-all">{grievance?.hash || '-'}</span></div>
        </div>
      </div>

      {status === 'resolved' && !grievance?.resolution_confirmed && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-6 text-center">
          <p className="text-yellow-800 mb-3 font-medium">Your complaint has been marked as resolved. Do you confirm?</p>
          <button onClick={handleConfirm} disabled={confirming}
            className="px-6 py-2 bg-accent text-white rounded-lg font-semibold hover:bg-emerald-600 disabled:opacity-50 transition-colors">
            {confirming ? 'Confirming...' : 'Yes, Confirm Resolution'}
          </button>
        </div>
      )}

      {status === 'closed' && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6 mb-6 text-center">
          <p className="text-green-800 font-medium text-lg">\u2705 This complaint has been resolved and confirmed. Thank you!</p>
        </div>
      )}

      <h3 className="text-lg font-heading font-semibold text-navy mb-4">Action Timeline</h3>
      <div className="space-y-4">
        {actions.length === 0 && <p className="text-gray-400 text-sm">No actions recorded yet.</p>}
        {actions.map((action, idx) => (
          <div key={action?.id || idx} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-navy text-white flex items-center justify-center text-sm">
                {ACTION_ICONS[action?.action_type] || '\u{25CF}'}
              </div>
              {idx < actions.length - 1 && <div className="w-0.5 flex-1 bg-gray-200 mt-1"></div>}
            </div>
            <div className="flex-1 pb-4">
              <p className="font-medium text-sm capitalize">{(action?.action_type || '').replace(/_/g, ' ')}</p>
              <p className="text-gray-500 text-xs">{action?.notes || ''}</p>
              <p className="text-gray-400 text-xs mt-1">{action?.created_at ? new Date(action.created_at).toLocaleString() : ''}</p>
              {action?.hash && <p className="text-gray-300 text-xs font-mono mt-0.5">Hash: {action.hash.slice(0, 16)}...</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
