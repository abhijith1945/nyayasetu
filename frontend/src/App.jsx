import React, { useState, useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import CitizenPortal from './pages/CitizenPortal'
import OfficerDashboard from './pages/OfficerDashboard'
import AssignmentsView from './pages/AssignmentsView'
import JusticeLinkPage from './pages/JusticeLinkPage'
import TrackGrievance from './pages/TrackGrievance'
import CommunityFeed from './pages/CommunityFeed'
import RailwayPortal from './pages/RailwayPortal'
import RailwayDashboard from './pages/RailwayDashboard'
import Login from './pages/Login'
import OfficerLogin from './pages/OfficerLogin'
import AppDemo from './pages/AppDemo'

function App() {
  const [dark, setDark] = useState(() => {
    try { return localStorage.getItem('nyayasetu-dark') === '1' } catch { return false }
  })
  const location = useLocation()

  useEffect(() => {
    // Demo mode: set a dummy token if not present (for testing)
    if (!localStorage.getItem('authToken')) {
      localStorage.setItem('authToken', 'demo-token-nyayasetu-2026')
      localStorage.setItem('user', JSON.stringify({ role: 'citizen', email: 'demo@nyayasetu.local' }))
    }
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    try { localStorage.setItem('nyayasetu-dark', dark ? '1' : '0') } catch {}
  }, [dark])

  // Hide navbar on login pages (demo mode - no auth required)
  const hideNavbar = location.pathname === '/login' || location.pathname === '/officer-login'

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {!hideNavbar && <Navbar dark={dark} onToggleDark={() => setDark(d => !d)} />}
      <main>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/officer-login" element={<OfficerLogin />} />
          <Route path="/" element={<CitizenPortal />} />
          <Route path="/officer" element={<OfficerDashboard />} />
          <Route path="/officer/assignments" element={<AssignmentsView />} />
          <Route path="/railway" element={<RailwayPortal />} />
          <Route path="/railway-officer" element={<RailwayDashboard />} />
          <Route path="/justice" element={<JusticeLinkPage />} />
          <Route path="/community" element={<CommunityFeed />} />
          <Route path="/track/:id" element={<TrackGrievance />} />
          <Route path="/demo" element={<AppDemo />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
