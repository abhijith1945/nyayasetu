import React, { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import CitizenPortal from './pages/CitizenPortal'
import OfficerDashboard from './pages/OfficerDashboard'
import JusticeLinkPage from './pages/JusticeLinkPage'
import TrackGrievance from './pages/TrackGrievance'
import CommunityFeed from './pages/CommunityFeed'

function App() {
  const [dark, setDark] = useState(() => {
    try { return localStorage.getItem('nyayasetu-dark') === '1' } catch { return false }
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    try { localStorage.setItem('nyayasetu-dark', dark ? '1' : '0') } catch {}
  }, [dark])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <Navbar dark={dark} onToggleDark={() => setDark(d => !d)} />
      <main>
        <Routes>
          <Route path="/" element={<CitizenPortal />} />
          <Route path="/officer" element={<OfficerDashboard />} />
          <Route path="/justice" element={<JusticeLinkPage />} />
          <Route path="/community" element={<CommunityFeed />} />
          <Route path="/track/:id" element={<TrackGrievance />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
