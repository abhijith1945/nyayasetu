import React, { useState, useEffect, useCallback } from 'react'
import { getLegalCases, addLegalCase, checkEligibility } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorCard from '../components/ErrorCard'
import Toast from '../components/Toast'

const API_BASE = 'http://localhost:8000/api'

export default function JusticeLinkPage() {
  const [activeTab, setActiveTab] = useState('cases')
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
  
  // Bail prediction
  const [bailRecommendations, setBailRecommendations] = useState([])
  const [bailLoading, setBailLoading] = useState(false)
  const [bailPredictionResult, setBailPredictionResult] = useState(null)
  const [modelInitialized, setModelInitialized] = useState(false)
  
  // Legal advice
  const [legalAdviceResult, setLegalAdviceResult] = useState(null)
  const [legalAdviceLoading, setLegalAdviceLoading] = useState(false)

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

  // Bail prediction form state
  const [bailForm, setBailForm] = useState({
    case_id: '',
    prisoner_name: '',
    age: 35,
    offence_category: 'theft',
    offence_severity: 3,
    prior_criminal_history: 'none',
    employment_status: 'employed',
    monthly_income: 50000,
    residential_stability: 'owned',
    years_in_current_city: 5,
    has_family_ties: true,
    has_guarantor: false,
    guarantor_income: 0,
    flight_risk: 'low',
    is_repeat_offender: false,
    days_between_arrest_and_trial: 120,
    credibility_score: 50,
  })

  // Legal advice form state
  const [legalForm, setLegalForm] = useState({
    query: '',
    case_type: '',
    ipc_section: '',
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

  // Initialize bail model
  const handleInitializeBailModel = async () => {
    setBailLoading(true)
    try {
      const response = await fetch(`${API_BASE}/legal/bail/initialize-model`, {
        method: 'POST',
      })
      const data = await response.json()
      if (data.success) {
        setToast({
          type: 'success',
          message: `✅ Model trained! Accuracy: ${(data.data.accuracy*100).toFixed(1)}%`,
        })
        setModelInitialized(true)
      } else {
        setToast({ type: 'error', message: 'Failed to initialize model' })
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Error initializing model' })
    } finally {
      setBailLoading(false)
    }
  }

  // Predict bail eligibility
  const handleBailPrediction = async (e) => {
    e.preventDefault()
    setBailLoading(true)
    try {
      const response = await fetch(`${API_BASE}/legal/bail/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bailForm),
      })
      const data = await response.json()
      if (data.success) {
        setBailPredictionResult(data.data)
        setToast({
          type: data.data.bail_eligible ? 'success' : 'info',
          message: data.data.recommendation,
        })
      } else {
        setToast({ type: 'error', message: data.error || 'Prediction failed' })
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Error predicting bail eligibility' })
    } finally {
      setBailLoading(false)
    }
  }

  // Get bail recommendations list
  const handleGetBailRecommendations = async () => {
    setBailLoading(true)
    try {
      const response = await fetch(`${API_BASE}/legal/bail/list`)
      const data = await response.json()
      if (data.success) {
        setBailRecommendations(data.data)
        setToast({
          type: 'success',
          message: `Found ${data.data.length} eligible persons for bail`,
        })
      } else {
        setToast({ type: 'error', message: 'Failed to fetch bail recommendations' })
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Error fetching recommendations' })
    } finally {
      setBailLoading(false)
    }
  }

  // Export bail list to Excel
  const handleExportBailExcel = async () => {
    setBailLoading(true)
    try {
      const response = await fetch(`${API_BASE}/legal/bail/export-excel`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `bail_recommendations_${new Date().toISOString().slice(0, 10)}.xlsx`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        a.remove()
        setToast({ type: 'success', message: '✅ Bail list exported to Excel' })
      } else {
        setToast({ type: 'error', message: 'Failed to export Excel file' })
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Error exporting bail list' })
    } finally {
      setBailLoading(false)
    }
  }

  // Get legal advice
  const handleGetLegalAdvice = async (e) => {
    e.preventDefault()
    setLegalAdviceLoading(true)
    try {
      const response = await fetch(`${API_BASE}/legal/advice/legal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(legalForm),
      })
      const data = await response.json()
      if (data.success) {
        setLegalAdviceResult(data.data)
        setToast({
          type: 'success',
          message: `Legal advice generated (${data.data.source})`,
        })
      } else {
        setToast({ type: 'error', message: data.error || 'Failed to get advice' })
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Error getting legal advice' })
    } finally {
      setLegalAdviceLoading(false)
    }
  }

  // Handle add case
  const handleAddCase = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await addLegalCase(form)
      if (res?.data?.success) {
        setToast({ type: 'success', message: '✅ Legal case added!' })
        setForm({
          prisoner_name: '',
          ward: '',
          ipc_section: '',
          max_sentence_years: '',
          detention_start: '',
          months_detained: '',
          dlsa_contact: '',
        })
        setShowAddModal(false)
        await fetchCases()
      } else {
        setToast({ type: 'error', message: res?.data?.error || 'Failed to add case' })
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Error adding case' })
    } finally {
      setLoading(false)
    }
  }

  // Handle explain case
  const handleExplainCase = async (caseItem) => {
    setSelectedCase(caseItem)
    setExplainLoading(true)
    try {
      const res = await checkEligibility(caseItem.id)
      if (res?.data?.success) {
        setExplanation(res.data.data?.explanation || 'No explanation available')
        setShowExplainModal(true)
      } else {
        setToast({ type: 'error', message: 'Failed to get explanation' })
      }
    } catch (err) {
      setToast({ type: 'error', message: 'Error getting explanation' })
    } finally {
      setExplainLoading(false)
    }
  }

  // Computed stats
  const totalCases = cases.length
  const eligibleCount = cases.filter((c) => c?.eligible_436a).length

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}

      {/* Header */}
      <div className="mb-8">
        <h1 className="font-heading text-3xl font-bold text-navy mb-2">⚖️ JusticeLink</h1>
        <p className="text-gray-600">AI-Powered Legal Support & Bail Prediction System</p>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-2 border-b border-gray-200 overflow-x-auto">
        {[
          { id: 'cases', label: '📋 Legal Cases', icon: '📋' },
          { id: 'bail-predict', label: '🔮 Predict Bail', icon: '🔮' },
          { id: 'bail-list', label: '👥 Bail List', icon: '👥' },
          { id: 'legal-advice', label: '⚖️ Legal Advice', icon: '⚖️' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-b-2 border-accent text-accent'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="space-y-6">

        {/* ─── LEGAL CASES TAB ─── */}
        {activeTab === 'cases' && (
          <div>
            <div className="mb-4 flex justify-between items-center">
              <h2 className="text-xl font-bold text-navy">Legal Cases (436A - Undertrial Ban)</h2>
              <button
                onClick={() => setShowAddModal(true)}
                className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent/90"
              >
                + Add Case
              </button>
            </div>

            {/* Stats */}
            <div className="mb-4 grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-white p-4 shadow-sm border-l-4 border-accent">
                <p className="text-3xl font-bold text-navy">{totalCases}</p>
                <p className="text-sm text-gray-600">Total Cases</p>
              </div>
              <div className="rounded-lg bg-green-50 p-4 shadow-sm border-l-4 border-green-500">
                <p className="text-3xl font-bold text-green-700">{eligibleCount}</p>
                <p className="text-sm text-gray-600">436A Eligible</p>
              </div>
            </div>

            {loading ? (
              <LoadingSpinner message="Loading cases..." />
            ) : error ? (
              <ErrorCard error={error} />
            ) : (
              <div className="grid gap-4">
                {cases.length === 0 ? (
                  <div className="rounded-lg bg-white p-6 text-center text-gray-500">
                    No legal cases yet
                  </div>
                ) : (
                  cases.map(caseItem => (
                    <div key={caseItem.id} className="rounded-lg bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start gap-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-navy">{caseItem.prisoner_name}</h3>
                          <p className="text-sm text-gray-600">IPC: {caseItem.ipc_section || 'N/A'}</p>
                          <p className="text-sm text-gray-600">Ward: {caseItem.ward || 'N/A'} | Detained: {caseItem.months_detained || 0} months</p>
                          <div className="mt-2 flex gap-2">
                            <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                              caseItem.eligible_436a
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}>
                              {caseItem.eligible_436a ? '✅ 436A Eligible' : '⚠️ Not 436A'}
                            </span>
                          </div>
                        </div>
                        {caseItem.eligible_436a && (
                          <button
                            onClick={() => handleExplainCase(caseItem)}
                            className="rounded-lg bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100"
                          >
                            Get Legal Aid
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}

        {/* ─── BAIL PREDICTION TAB ─── */}
        {activeTab === 'bail-predict' && (
          <div>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-navy">🔮 Bail Eligibility Predictor</h2>
              <button
                onClick={handleInitializeBailModel}
                disabled={bailLoading || modelInitialized}
                className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:bg-gray-400"
              >
                {modelInitialized ? '✅ Model Ready' : '🤖 Initialize AI Model'}
              </button>
            </div>

            {bailPredictionResult ? (
              <div className="mb-6 rounded-lg bg-white p-6 shadow-md border-l-4 border-accent">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-navy">Prediction Result</h3>
                    <p className="text-sm text-gray-600">Case: {bailPredictionResult.case_id}</p>
                  </div>
                  <span className={`px-4 py-2 rounded-full font-bold text-white ${
                    bailPredictionResult.bail_eligible
                      ? 'bg-green-500'
                      : 'bg-red-500'
                  }`}>
                    {bailPredictionResult.bail_eligible ? '✅ ELIGIBLE' : '❌ NOT ELIGIBLE'}
                  </span>
                </div>
                <p className="text-gray-700 mb-4">{bailPredictionResult.reasoning}</p>
                <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                  <div className="bg-gray-50 p-3 rounded">
                    <p className="text-gray-600 text-xs">Model Type</p>
                    <p className="font-semibold">{bailPredictionResult.model_type}</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <p className="text-gray-600 text-xs">Confidence</p>
                    <p className="font-semibold">{(bailPredictionResult.confidence * 100).toFixed(1)}%</p>
                  </div>
                </div>
                <button
                  onClick={() => setBailPredictionResult(null)}
                  className="w-full rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
                >
                  Clear Result
                </button>
              </div>
            ) : null}

            <form onSubmit={handleBailPrediction} className="rounded-lg bg-white p-6 shadow-md space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="Case ID"
                  value={bailForm.case_id}
                  onChange={(e) => setBailForm({ ...bailForm, case_id: e.target.value })}
                  className="rounded border border-gray-300 px-3 py-2 text-sm"
                  required
                />
                <input
                  type="text"
                  placeholder="Prisoner Name"
                  value={bailForm.prisoner_name}
                  onChange={(e) => setBailForm({ ...bailForm, prisoner_name: e.target.value })}
                  className="rounded border border-gray-300 px-3 py-2 text-sm"
                  required
                />
                <input
                  type="number"
                  placeholder="Age"
                  value={bailForm.age}
                  onChange={(e) => setBailForm({ ...bailForm, age: parseInt(e.target.value) })}
                  className="rounded border border-gray-300 px-3 py-2 text-sm"
                />
                <select
                  value={bailForm.offence_severity}
                  onChange={(e) => setBailForm({ ...bailForm, offence_severity: parseInt(e.target.value) })}
                  className="rounded border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value={1}>Severity 1 (Low)</option>
                  <option value={2}>Severity 2</option>
                  <option value={3}>Severity 3</option>
                  <option value={4}>Severity 4</option>
                  <option value={5}>Severity 5 (High)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <select
                  value={bailForm.prior_criminal_history}
                  onChange={(e) => setBailForm({ ...bailForm, prior_criminal_history: e.target.value })}
                  className="rounded border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value="none">No Prior History</option>
                  <option value="minor">Minor Prior</option>
                  <option value="moderate">Moderate Prior</option>
                  <option value="serious">Serious Prior</option>
                </select>
                <select
                  value={bailForm.employment_status}
                  onChange={(e) => setBailForm({ ...bailForm, employment_status: e.target.value })}
                  className="rounded border border-gray-300 px-3 py-2 text-sm"
                >
                  <option>employed</option>
                  <option>self_employed</option>
                  <option>unemployed</option>
                  <option>student</option>
                </select>
                <input
                  type="number"
                  placeholder="Monthly Income"
                  value={bailForm.monthly_income}
                  onChange={(e) => setBailForm({ ...bailForm, monthly_income: parseInt(e.target.value) })}
                  className="rounded border border-gray-300 px-3 py-2 text-sm"
                />
                <select
                  value={bailForm.flight_risk}
                  onChange={(e) => setBailForm({ ...bailForm, flight_risk: e.target.value })}
                  className="rounded border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value="low">Low Flight Risk</option>
                  <option value="medium">Medium Flight Risk</option>
                  <option value="high">High Flight Risk</option>
                  <option value="very_high">Very High Flight Risk</option>
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <label className="flex items-center gap-2 flex-1">
                  <input
                    type="checkbox"
                    checked={bailForm.has_family_ties}
                    onChange={(e) => setBailForm({ ...bailForm, has_family_ties: e.target.checked })}
                  />
                  <span className="text-sm">Has Family Ties</span>
                </label>
                <label className="flex items-center gap-2 flex-1">
                  <input
                    type="checkbox"
                    checked={bailForm.is_repeat_offender}
                    onChange={(e) => setBailForm({ ...bailForm, is_repeat_offender: e.target.checked })}
                  />
                  <span className="text-sm">Repeat Offender</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={bailLoading || !modelInitialized}
                className="w-full rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent/90 disabled:bg-gray-400"
              >
                {bailLoading ? '⏳ Processing...' : '🔮 Predict Bail Eligibility'}
              </button>
            </form>
          </div>
        )}

        {/* ─── BAIL LIST TAB ─── */}
        {activeTab === 'bail-list' && (
          <div>
            <div className="mb-4 flex justify-between items-center gap-3">
              <h2 className="text-xl font-bold text-navy">👥 Eligible Persons for Bail</h2>
              <div className="flex gap-2">
                <button
                  onClick={handleGetBailRecommendations}
                  disabled={bailLoading}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {bailLoading ? '⏳ Loading...' : '🔄 Fetch List'}
                </button>
                <button
                  onClick={handleExportBailExcel}
                  disabled={bailLoading || bailRecommendations.length === 0}
                  className="rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700 disabled:bg-gray-400"
                >
                  📊 Export Excel
                </button>
              </div>
            </div>

            {bailRecommendations.length === 0 ? (
              <div className="rounded-lg bg-white p-6 text-center text-gray-500">
                No bail recommendations loaded. Click "Fetch List" to load eligible persons.
              </div>
            ) : (
              <div className="grid gap-3 max-h-[600px] overflow-y-auto">
                {bailRecommendations.map((person, idx) => (
                  <div key={idx} className="rounded-lg bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start gap-4">
                      <div className="flex-1 text-sm">
                        <h3 className="font-semibold text-navy">{person.citizen_name}</h3>
                        <p className="text-gray-600">Phone: {person.phone}</p>
                        <p className="text-gray-600">Ward: {person.ward} | Category: {person.category}</p>
                        {person.recommended_bail_amount > 0 && (
                          <p className="text-green-700 font-semibold mt-1">
                            💰 Recommended Bail: ₹{person.recommended_bail_amount.toLocaleString()}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <span className="inline-block rounded-full bg-green-100 px-3 py-1 text-sm font-bold text-green-700">
                          {(person.recommendation_confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ─── LEGAL ADVICE TAB ─── */}
        {activeTab === 'legal-advice' && (
          <div>
            <h2 className="text-xl font-bold text-navy mb-4">⚖️ AI Legal Advice (GenAI)</h2>

            {legalAdviceResult && (
              <div className="mb-6 rounded-lg bg-white p-6 shadow-md border-l-4 border-accent">
                <div className="mb-4">
                  <h3 className="text-lg font-bold text-navy mb-2">Legal Advice Generated</h3>
                  <span className="inline-block text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700 font-semibold">
                    {legalAdviceResult.source}
                  </span>
                </div>
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed mb-4">{legalAdviceResult.advice}</p>
                <div className="bg-yellow-50 border border-yellow-200 rounded px-3 py-2 text-xs text-yellow-800">
                  ⚠️ DISCLAIMER: This is general information. Always consult a licensed lawyer.
                </div>
                <button
                  onClick={() => setLegalAdviceResult(null)}
                  className="mt-4 w-full rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
                >
                  Clear Advice
                </button>
              </div>
            )}

            <form onSubmit={handleGetLegalAdvice} className="rounded-lg bg-white p-6 shadow-md space-y-4">
              <div>
                <label className="block text-sm font-semibold text-navy mb-2">Your Legal Question *</label>
                <textarea
                  placeholder="Ask your legal question..."
                  value={legalForm.query}
                  onChange={(e) => setLegalForm({ ...legalForm, query: e.target.value })}
                  className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
                  rows={4}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-navy mb-2">Case Type</label>
                  <select
                    value={legalForm.case_type}
                    onChange={(e) => setLegalForm({ ...legalForm, case_type: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
                  >
                    <option value="">Select case type...</option>
                    <option value="bail">Bail</option>
                    <option value="criminal">Criminal</option>
                    <option value="civil">Civil</option>
                    <option value="property">Property</option>
                    <option value="labour">Labour</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-navy mb-2">IPC Section</label>
                  <input
                    type="text"
                    placeholder="e.g., 420, 302"
                    value={legalForm.ipc_section}
                    onChange={(e) => setLegalForm({ ...legalForm, ipc_section: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={legalAdviceLoading || !legalForm.query}
                className="w-full rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent/90 disabled:bg-gray-400"
              >
                {legalAdviceLoading ? '⏳ Generating advice...' : '⚖️ Get Legal Advice'}
              </button>
            </form>
          </div>
        )}
      </div>

      {/* ─── ADD CASE MODAL ─── */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 font-heading text-xl font-bold text-navy">Add Legal Case</h2>

            <form onSubmit={handleAddCase} className="space-y-3">
              <input
                type="text"
                placeholder="Prisoner Name *"
                value={form.prisoner_name}
                onChange={(e) => setForm({ ...form, prisoner_name: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                required
              />
              <input
                type="text"
                placeholder="Ward"
                value={form.ward}
                onChange={(e) => setForm({ ...form, ward: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
              <input
                type="text"
                placeholder="IPC Section"
                value={form.ipc_section}
                onChange={(e) => setForm({ ...form, ipc_section: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="number"
                  placeholder="Max Sentence (years)"
                  value={form.max_sentence_years}
                  onChange={(e) => setForm({ ...form, max_sentence_years: e.target.value })}
                  className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
                />
                <input
                  type="number"
                  placeholder="Months Detained"
                  value={form.months_detained}
                  onChange={(e) => setForm({ ...form, months_detained: e.target.value })}
                  className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
                />
              </div>
              <input
                type="text"
                placeholder="DLSA Contact"
                value={form.dlsa_contact}
                onChange={(e) => setForm({ ...form, dlsa_contact: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="rounded-lg px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent/90"
                >
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
            <h2 className="mb-4 font-heading text-xl font-bold text-navy">
              436A Legal Explanation
            </h2>

            {explainLoading ? (
              <LoadingSpinner message="Getting explanation..." />
            ) : (
              <div className="prose prose-sm max-w-none font-body text-gray-700 whitespace-pre-wrap leading-relaxed">
                {explanation}
              </div>
            )}

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setShowExplainModal(false)}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
