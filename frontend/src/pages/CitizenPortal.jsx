import React, { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitGrievance } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorCard from '../components/ErrorCard'
import Toast from '../components/Toast'
import ReceiptCard from '../components/ReceiptCard'

const WARDS = [
  'Ward 1 (Kazhakoottam)',
  'Ward 2 (Technopark)',
  'Ward 3 (Pattom)',
  'Ward 4 (Vanchiyoor)',
  'Ward 5 (Palayam)',
  'Ward 6 (Karamana)',
  'Ward 7 (Nemom)',
  'Ward 8 (Kovalam)',
]

const LANGUAGES = ['English', 'Malayalam', 'Hindi']

export default function CitizenPortal() {
  const navigate = useNavigate()
  const recognitionRef = useRef(null)

  // Form state
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [ward, setWard] = useState('')
  const [description, setDescription] = useState('')
  const [language, setLanguage] = useState('English')

  // UI state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)
  const [receipt, setReceipt] = useState(null)
  const [listening, setListening] = useState(false)

  // Check speech recognition support
  const SpeechRecognition =
    typeof window !== 'undefined'
      ? window.SpeechRecognition || window.webkitSpeechRecognition
      : null

  const startListening = useCallback(() => {
    if (!SpeechRecognition) {
      setToast({ message: 'Use Chrome for voice input', type: 'error' })
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognition.lang = language === 'Malayalam' ? 'ml-IN' : language === 'Hindi' ? 'hi-IN' : 'en-IN'
      recognition.interimResults = true
      recognition.continuous = true

      recognition.onstart = () => setListening(true)

      recognition.onresult = (event) => {
        let transcript = ''
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript
        }
        setDescription(transcript)
      }

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setListening(false)
        if (event.error !== 'aborted') {
          setToast({ message: `Voice error: ${event.error}`, type: 'error' })
        }
      }

      recognition.onend = () => setListening(false)

      recognitionRef.current = recognition
      recognition.start()
    } catch (err) {
      console.error('Speech recognition start error:', err)
      setToast({ message: 'Could not start voice input', type: 'error' })
    }
  }, [SpeechRecognition, language])

  const stopListening = useCallback(() => {
    try {
      recognitionRef.current?.stop()
    } catch {
      // ignore
    }
    setListening(false)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!name.trim() || !ward || !description.trim()) {
      setToast({ message: 'Please fill in name, ward, and description', type: 'error' })
      return
    }

    setLoading(true)
    try {
      const result = await submitGrievance({
        citizen_name: name.trim(),
        phone: phone.trim() || null,
        ward,
        description: description.trim(),
      })

      const data = result?.data?.data || result?.data
      if (data?.grievance) {
        setReceipt({
          id: data.grievance.id,
          hash: data.hash || data.grievance.hash,
          category: data.ai_analysis?.category || data.grievance.category,
          urgency: data.ai_analysis?.urgency || data.grievance.urgency,
        })
        setToast({ message: 'Complaint submitted successfully!', type: 'success' })
        // Reset form
        setName('')
        setPhone('')
        setWard('')
        setDescription('')
      } else {
        setError('Submission returned unexpected data. Please try again.')
      }
    } catch (err) {
      console.error('Submit error:', err)
      setError(err?.message || 'Failed to submit complaint. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // If receipt is shown, display it
  if (receipt) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        {toast && (
          <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
        )}
        <ReceiptCard
          grievance={receipt}
          onTrack={(id) => navigate(`/track/${id}`)}
        />
        <button
          onClick={() => setReceipt(null)}
          className="mx-auto mt-6 block text-sm text-accent hover:underline font-body"
        >
          Submit another complaint
        </button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
      )}

      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="font-heading text-3xl font-bold text-navy">
          File a Grievance
        </h1>
        <p className="mt-2 font-body text-gray-500">
          Your voice. Our governance. Speak or type your complaint below.
        </p>
      </div>

      {/* Language selector */}
      <div className="mb-6 flex items-center justify-center gap-2">
        {LANGUAGES.map((lang) => (
          <button
            key={lang}
            onClick={() => setLanguage(lang)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium font-body transition-colors ${
              language === lang
                ? 'bg-navy text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {lang}
          </button>
        ))}
      </div>

      {/* Voice button */}
      <div className="mb-8 flex flex-col items-center">
        <button
          onClick={listening ? stopListening : startListening}
          className={`relative flex h-20 w-20 items-center justify-center rounded-full text-white shadow-lg transition-all focus:outline-none focus:ring-4 focus:ring-accent/50 ${
            listening
              ? 'bg-critical mic-pulse scale-110'
              : 'bg-accent hover:bg-accent/90 hover:scale-105'
          }`}
          aria-label={listening ? 'Stop recording' : 'Start voice input'}
        >
          <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        </button>
        <p className={`mt-3 text-sm font-body ${listening ? 'text-critical font-semibold animate-pulse' : 'text-gray-400'}`}>
          {listening ? 'Listening... tap to stop' : 'Tap to speak your complaint'}
        </p>
        {!SpeechRecognition && (
          <p className="mt-1 text-xs text-orange-500 font-body">
            Use Chrome for voice input
          </p>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-6">
          <ErrorCard message={error} onRetry={() => setError(null)} />
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Name */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 font-body">
            Your Name <span className="text-critical">*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your full name"
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-body text-gray-900 placeholder-gray-400 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
            required
            disabled={loading}
          />
        </div>

        {/* Phone */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 font-body">
            Phone Number <span className="text-xs text-gray-400">(for SMS confirmation)</span>
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+91XXXXXXXXXX"
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-body text-gray-900 placeholder-gray-400 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
            disabled={loading}
          />
        </div>

        {/* Ward */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 font-body">
            Ward <span className="text-critical">*</span>
          </label>
          <select
            value={ward}
            onChange={(e) => setWard(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-body text-gray-900 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
            required
            disabled={loading}
          >
            <option value="">Select your ward</option>
            {WARDS.map((w) => (
              <option key={w} value={w}>{w}</option>
            ))}
          </select>
        </div>

        {/* Description */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 font-body">
            Complaint Description <span className="text-critical">*</span>
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your complaint in detail..."
            rows={5}
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-body text-gray-900 placeholder-gray-400 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
            required
            disabled={loading}
          />
          <p className="mt-1 text-xs text-gray-400 font-body">
            {description.length} characters
          </p>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !name.trim() || !ward || !description.trim()}
          className="w-full rounded-lg bg-accent px-6 py-3 text-base font-semibold text-white shadow-sm transition-all hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Analysing your complaint...' : 'Submit Complaint'}
        </button>
      </form>

      {loading && (
        <div className="mt-6">
          <LoadingSpinner message="AI is analysing your complaint..." />
        </div>
      )}
    </div>
  )
}
