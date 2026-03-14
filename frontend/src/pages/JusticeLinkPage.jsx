import React, { useState, useEffect, useCallback } from 'react'
import { getLegalCases, addLegalCase, checkEligibility } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorCard from '../components/ErrorCard'
import Toast from '../components/Toast'

export default function JusticeLinkPage() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false)
  const [showExplainModal, setShowExplainModal] = useState(false)
  const [explanation, setExplanation] = useState('')
  const [explainLoading, setExplainLoading] = useState(false)
  const [selectedCase, setSelectedCase] = useState(null)

  // Add form state
  const [form, setForm] = useState({
    prisoner_name: '',
    ward: '',
    ipc_section: '',
    max_sentence_years: '',
    detention_start: '',
    months_detained: '',
    dlsa_contact: '',
  })

  const fetchCases = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getLegalCases()
      setCases(res?.data?.data || res?.data || [])
    } catch (err) {
      console.error('Legal cases fetch error:', err)
      setError(err?.message || 'Failed to load legal cases')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    try {
      fetchCases()
    } catch (err) {
      console.error('useEffect legal error:', err)
    }
  }, [fetchCases])

  // Computed stats
  const totalCases = cases.length
  const eligibleCount = cases.filter((c) => c?.eligible_436a).length
  const avgDetention = totalCases > 0
    ? Math.round(cases.reduce((sum, c) => sum + (c?.months_detained || 0), 0) / totalCases)
    : 0

  // Handle add case
  const handleAddCase = async (e) => {
    e.preventDefault()
    try {
      await addLegalCase({
        ...form,
        max_sentence_years: Number(form.max_sentence_years) || 0,
        months_detained: Number(form.months_detained) || 0,
      })
      setToast({ message: 'Legal case added successfully', type: 'success' })
      setShowAddModal(false)
      setForm({
        prisoner_name: '', ward: '', ipc_section: '',
        max_sentence_years: '', detention_start: '', months_detained: '', dlsa_contact: '',
      })
      fetchCases()
    } catch (err) {
      console.error('Add case error:', err)
      setToast({ message: err?.message || 'Failed to add case', type: 'error' })
    }
  }

  // Handle explain 436A
  const handleExplain = async (legalCase) => {
    setSelectedCase(legalCase)
    setShowExplainModal(true)
    setExplainLoading(true)
    setExplanation('')
    try {
      const res = await checkEligibility(legalCase.id)
      setExplanation(res?.data?.data?.explanation || res?.data?.explanation || 'No explanation available.')
    } catch (err) {
      console.error('Explain error:', err)
      setExplanation('Failed to get legal explanation. Please try again.')
    } finally {
      setExplainLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
      )}

      {/* Header */}
      <div className="mb-8">
        <h1 className="font-heading text-3xl font-bold text-navy">
          Justice-Link
        </h1>
        <p className="mt-1 font-body text-gray-500">
          Undertrial Prisoner Rights — Section 436A CrPC
        </p>
      </div>

      {/* Stats bar */}
      <div className="mb-8 grid grid-cols-3 gap-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-center shadow-sm">
          <p className="text-2xl font-heading font-bold text-navy">{totalCases}</p>
          <p className="text-xs text-gray-500 font-body">Total Cases</p>
        </div>
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-center shadow-sm">
          <p className="text-2xl font-heading font-bold text-accent">{eligibleCount}</p>
          <p className="text-xs text-gray-500 font-body">436A Eligible</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-center shadow-sm">
          <p className="text-2xl font-heading font-bold text-navy">{avgDetention}</p>
          <p className="text-xs text-gray-500 font-body">Avg Detention (months)</p>
        </div>
      </div>

      {/* Add case button */}
      <div className="mb-4 flex justify-end">
        <button
          onClick={() => setShowAddModal(true)}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent/90 transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
        >
          + Add New Case
        </button>
      </div>

      {/* Error */}
      {error && <ErrorCard message={error} onRetry={fetchCases} />}

      {/* Loading */}
      {loading ? (
        <LoadingSpinner message="Loading legal cases..." />
      ) : (
        /* Table */
        <div className="table-scroll rounded-lg border border-gray-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-gray-200 text-sm font-body">
            <thead className="bg-gray-50">
              <tr>
                {['Prisoner Name', 'Ward', 'IPC Section', 'Max Sentence', 'Months Detained', '436A Status', 'DLSA Contact', 'Actions'].map((h) => (
                  <th key={h} className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-400">No legal cases found.</td>
                </tr>
              ) : (
                cases.map((c, idx) => {
                  const eligible = c?.eligible_436a
                  return (
                    <tr
                      key={c?.id || idx}
                      className={`transition-colors hover:bg-gray-50 ${eligible ? 'bg-green-50/50' : ''}`}
                    >
                      <td className="whitespace-nowrap px-4 py-3 font-medium text-gray-900">
                        {c?.prisoner_name || '--'}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-gray-600">
                        {c?.ward || '--'}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-gray-600">
                        {c?.ipc_section || '--'}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-gray-600">
                        {c?.max_sentence_years ? `${c.max_sentence_years} yrs` : '--'}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-gray-600">
                        {c?.months_detained ?? '--'}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3">
                        {eligible ? (
                          <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-bold text-green-700">
                            ELIGIBLE
                          </span>
                        ) : (
                          <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-500">
                            Not yet
                          </span>
                        )}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-xs text-gray-500">
                        {c?.dlsa_contact || '--'}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3">
                        {eligible && (
                          <button
                            onClick={() => handleExplain(c)}
                            className="rounded-md bg-accent px-3 py-1 text-xs font-semibold text-white hover:bg-accent/90 transition-colors focus:outline-none"
                          >
                            Get Legal Aid
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* ─── ADD CASE MODAL ─── */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-heading text-xl font-bold text-navy">Add New Case</h2>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
            </div>
            <form onSubmit={handleAddCase} className="space-y-3">
              {[
                { key: 'prisoner_name', label: 'Prisoner Name', type: 'text', required: true },
                { key: 'ward', label: 'Ward', type: 'text' },
                { key: 'ipc_section', label: 'IPC Section', type: 'text' },
                { key: 'max_sentence_years', label: 'Max Sentence (years)', type: 'number' },
                { key: 'detention_start', label: 'Detention Start Date', type: 'date' },
                { key: 'months_detained', label: 'Months Detained', type: 'number' },
                { key: 'dlsa_contact', label: 'DLSA Contact', type: 'text' },
              ].map(({ key, label, type, required }) => (
                <div key={key}>
                  <label className="mb-1 block text-sm font-medium text-gray-700 font-body">{label}</label>
                  <input
                    type={type}
                    value={form[key]}
                    onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                    required={required}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-body focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
                  />
                </div>
              ))}
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowAddModal(false)} className="rounded-lg px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100">
                  Cancel
                </button>
                <button type="submit" className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent/90">
                  Add Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ─── EXPLAIN MODAL ─── */}
      {showExplainModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg max-h-[80vh] overflow-auto rounded-xl bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-heading text-xl font-bold text-navy">
                436A Legal Aid — {selectedCase?.prisoner_name || 'Case'}
              </h2>
              <button onClick={() => setShowExplainModal(false)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
            </div>

            {explainLoading ? (
              <LoadingSpinner message="Getting legal explanation..." />
            ) : (
              <div className="prose prose-sm max-w-none font-body text-gray-700 whitespace-pre-wrap leading-relaxed">
                {explanation}
              </div>
            )}

            <div className="mt-4 flex justify-end">
              <button onClick={() => setShowExplainModal(false)} className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
