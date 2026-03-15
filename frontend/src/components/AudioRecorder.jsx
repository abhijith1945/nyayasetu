import React, { useState, useRef } from 'react'

export default function AudioRecorder({ onTranscribed, disabled = false, language = 'en' }) {
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [recordingLevelPercent, setRecordingLevelPercent] = useState(0)
  const [useWebSpeech, setUseWebSpeech] = useState(true)
  
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)
  const recognitionRef = useRef(null)
  const streamRef = useRef(null)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const animationIdRef = useRef(null)

  // Initialize Web Speech Recognition
  const createWebSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) return null
    
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 1
    recognition.language = language === 'ml' ? 'ml-IN' : 'en-US'
    
    return recognition
  }

  // Monitor audio levels
  const monitorAudioLevels = (stream) => {
    try {
      if (audioContextRef.current) return
      
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
      analyserRef.current = audioContextRef.current.createAnalyser()
      const microphone = audioContextRef.current.createMediaStreamSource(stream)
      microphone.connect(analyserRef.current)
      analyserRef.current.fftSize = 256
      
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
      
      const checkLevel = () => {
        if (!analyserRef.current) return
        analyserRef.current.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        setRecordingLevelPercent(Math.min(100, Math.round((average / 255) * 100)))
        animationIdRef.current = requestAnimationFrame(checkLevel)
      }
      
      checkLevel()
    } catch (err) {
      console.warn('Audio monitoring failed:', err)
    }
  }

  const cleanupAudioMonitoring = () => {
    if (animationIdRef.current) {
      cancelAnimationFrame(animationIdRef.current)
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    analyserRef.current = null
    setRecordingLevelPercent(0)
  }

  const startRecordingWebSpeech = async () => {
    try {
      const recognition = createWebSpeechRecognition()
      if (!recognition) {
        onTranscribed({ error: 'Web Speech API not supported. Try Chrome or Edge.' })
        return
      }

      recognitionRef.current = recognition
      let transcript = ''

      recognition.onstart = () => {
        setIsRecording(true)
        setIsTranscribing(true)
        setRecordingTime(0)
        console.log('🎙️ Web Speech started')
      }

      recognition.onresult = (event) => {
        transcript = ''
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript + ' '
        }
      }

      recognition.onend = async () => {
        const finalTranscript = transcript.trim()
        
        if (!finalTranscript) {
          onTranscribed({ error: 'No speech detected. Please try again.' })
          setIsRecording(false)
          setIsTranscribing(false)
          return
        }

        let finalText = finalTranscript

        // Translate Malayalam if needed
        if (language === 'ml') {
          try {
            const token = localStorage.getItem('authToken') || 'demo-token'
            const response = await fetch('http://localhost:8000/api/translate-from-malayalam', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ text: finalTranscript })
            })
            const result = await response.json()
            if (result.success && result.data?.english) {
              finalText = result.data.english
            }
          } catch (err) {
            console.warn('Translation failed:', err)
          }
        }

        setIsRecording(false)
        setIsTranscribing(false)
        onTranscribed({ text: finalText })
      }

      recognition.onerror = (event) => {
        let errorMsg = 'Error'
        switch(event.error) {
          case 'no-speech':
            errorMsg = 'No speech detected. Speak clearly and try again.'
            break
          case 'audio-capture':
            errorMsg = 'Microphone not found. Check browser permissions.'
            break
          case 'not-allowed':
            errorMsg = 'Microphone access denied. Allow in browser settings.'
            break
          case 'network':
            errorMsg = 'Network error. Check internet connection.'
            break
          default:
            errorMsg = `Error: ${event.error}`
        }
        
        setIsRecording(false)
        setIsTranscribing(false)
        onTranscribed({ error: errorMsg })
      }

      recognition.start()
      setRecordingTime(0)
      timerRef.current = setInterval(() => {
        setRecordingTime(t => {
          if (t >= 300) {
            recognition.stop()
            return 300
          }
          return t + 1
        })
      }, 1000)
    } catch (err) {
      console.error('Web Speech error:', err)
      onTranscribed({ error: `Microphone error: ${err.message}` })
    }
  }

  const startRecordingMediaRecorder = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      
      // Monitor audio levels
      monitorAudioLevels(stream)

      const mediaRecorder = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        cleanupAudioMonitoring()
        stream.getTracks().forEach(track => track.stop())
        streamRef.current = null

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await transcribeAudio(audioBlob)
      }

      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start()
      
      setIsRecording(true)
      setRecordingTime(0)
      timerRef.current = setInterval(() => {
        setRecordingTime(t => {
          if (t >= 300) {
            mediaRecorder.stop()
            return 300
          }
          return t + 1
        })
      }, 1000)
    } catch (err) {
      console.error('Recorder error:', err)
      onTranscribed({ error: 'Microphone access denied.' })
    }
  }

  const startRecording = () => {
    if (useWebSpeech) {
      startRecordingWebSpeech()
    } else {
      startRecordingMediaRecorder()
    }
  }

  const stopRecording = () => {
    if (timerRef.current) clearInterval(timerRef.current)

    if (useWebSpeech && recognitionRef.current) {
      recognitionRef.current.stop()
    } else if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }

    cleanupAudioMonitoring()
  }

  const transcribeAudio = async (audioBlob) => {
    setIsTranscribing(true)
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'audio.webm')
      
      const token = localStorage.getItem('authToken') || 'demo-token'
      const response = await fetch('http://localhost:8000/api/audio/transcribe', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      const result = await response.json()
      
      if (!result.success || !result.data?.text) {
        onTranscribed({ error: 'Transcription failed. Try Web Speech mode.' })
        setIsTranscribing(false)
        return
      }
      
      let finalText = result.data.text

      if (language === 'ml') {
        try {
          const translateResponse = await fetch('http://localhost:8000/api/translate-from-malayalam', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ text: result.data.text })
          })
          const translateResult = await translateResponse.json()
          if (translateResult.success && translateResult.data?.english) {
            finalText = translateResult.data.english
          }
        } catch (err) {
          console.warn('Translation error:', err)
        }
      }

      onTranscribed({ text: finalText })
      setIsTranscribing(false)
    } catch (err) {
      console.error('Transcription error:', err)
      onTranscribed({ error: 'Failed to transcribe audio.' })
      setIsTranscribing(false)
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="flex flex-col items-center gap-3">
      {/* Control Bar */}
      <div className="flex gap-2 items-center justify-center flex-wrap">
        {/* Mode Toggle */}
        <button
          type="button"
          onClick={() => !isRecording && setUseWebSpeech(!useWebSpeech)}
          disabled={disabled || isRecording}
          title={useWebSpeech ? 'Web Speech API (native)' : 'Whisper API (AI)'}
          className={`px-3 py-1 rounded text-xs font-bold transition ${
            useWebSpeech
              ? 'bg-green-100 text-green-700 hover:bg-green-200'
              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
          }`}
        >
          {useWebSpeech ? '🌐 Web Speech' : '🎙️ Whisper'}
        </button>
      </div>

      {/* Recording Mode Info */}
      <div className="text-xs text-gray-500 font-medium">
        {useWebSpeech ? 'Browser-based (Web Speech API)' : 'AI-powered (Whisper)'}
      </div>

      {/* Microphone Button */}
      <button
        type="button"
        onClick={isRecording || isTranscribing ? stopRecording : startRecording}
        disabled={disabled || isTranscribing}
        className={`relative flex h-16 w-16 items-center justify-center rounded-full shadow-lg transition-all focus:outline-none focus:ring-4 focus:ring-offset-2 ${
          isRecording
            ? 'bg-critical text-white focus:ring-critical/50 animate-pulse'
            : isTranscribing
            ? 'bg-orange-500 text-white focus:ring-orange-500/50 cursor-wait'
            : 'bg-accent text-white hover:bg-accent/90 hover:scale-105 focus:ring-accent/50'
        }`}
      >
        {isTranscribing ? (
          <svg className="h-6 w-6 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        ) : (
          <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        )}
      </button>

      {/* Recording Status */}
      {isRecording && (
        <div className="text-center">
          <p className="text-sm font-bold text-critical animate-pulse">
            🔴 Recording: {formatTime(recordingTime)}
          </p>
          {recordingLevelPercent > 0 && (
            <div className="w-32 h-1 bg-gray-200 rounded mt-1 overflow-hidden">
              <div 
                className="h-full bg-critical transition-all"
                style={{ width: `${recordingLevelPercent}%` }}
              />
            </div>
          )}
          <p className="text-xs text-gray-500 mt-1">(Tap to stop)</p>
        </div>
      )}

      {isTranscribing && !isRecording && (
        <p className="text-sm text-orange-600 font-medium animate-pulse">
          {useWebSpeech ? '⏳ Processing speech...' : '⏳ Converting audio...'}
        </p>
      )}
    </div>
  )
}
