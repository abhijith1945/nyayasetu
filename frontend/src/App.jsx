import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import CitizenPortal from './pages/CitizenPortal'
import OfficerDashboard from './pages/OfficerDashboard'
import JusticeLinkPage from './pages/JusticeLinkPage'
import TrackGrievance from './pages/TrackGrievance'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<CitizenPortal />} />
          <Route path="/officer" element={<OfficerDashboard />} />
          <Route path="/justice" element={<JusticeLinkPage />} />
          <Route path="/track/:id" element={<TrackGrievance />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
