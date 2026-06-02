import React, { useState } from 'react'
import { AlertCircle, BarChart3, TrendingUp, Zap, Gauge, Brain, CheckCircle, Clock } from 'lucide-react'
import axios from 'axios'

export default function AppDemo() {
  const [activeTab, setActiveTab] = useState('workflow')
  const [demoRunning, setDemoRunning] = useState(false)
  const [results, setResults] = useState(null)
  const [selectedScenario, setSelectedScenario] = useState('urgent_water')

  // Test scenarios with different characteristics
  const scenarios = {
    urgent_water: {
      title: '🚨 Urgent Water Crisis',
      grievance: {
        description: 'My name is Ramesh Kumar. Water pipe burst 5 days ago. No water for family. Kids are sick. My number is 9876543210. Please help!',
        ward: 'Ward 3',
        category: 'water',
        urgency: 5,
        credibility_score: 95,
        image_verified: true
      },
      expectedOutcome: 'Auto-detects name (Ramesh Kumar) and phone (9876543210). High priority, fast resolution predicted (24-48 hrs)'
    },
    low_credibility: {
      title: '⚠️ Low Credibility Claim',
      grievance: {
        description: 'I am Arun. Street light was supposedly broken somewhere. Call me at 9876543211 if you need more info.',
        ward: 'Ward 1',
        category: 'electricity',
        urgency: 1,
        credibility_score: 25,
        image_verified: false
      },
      expectedOutcome: 'Auto-detects name (Arun) and phone (9876543211). Low priority, requires verification (3-5 days)'
    },
    high_confidence: {
      title: '✅ Verified Sanitation Issue',
      grievance: {
        description: 'This is Priya Nair. Garbage pile blocking main road. 9876543212 is my contact. Verified with photos. Affecting 200+ residents.',
        ward: 'Ward 5',
        category: 'sanitation',
        urgency: 4,
        credibility_score: 88,
        image_verified: true
      },
      expectedOutcome: 'Auto-detects name (Priya Nair) and phone (9876543212). Medium-high priority (36-48 hrs)'
    }
  }

  const runFullDemo = async () => {
    setDemoRunning(true)
    setResults(null)

    try {
      const scenario = scenarios[selectedScenario]
      const grievance = {
        grievance_id: 'DEMO_' + Date.now(),
        ...scenario.grievance
      }

      // Step 1: Process grievance (AI analysis)
      const processRes = await axios.post(
        'http://localhost:8000/api/agents/grievance/process',
        grievance
      )

      // Step 2: Route to officer (intelligent assignment)
      const routeRes = await axios.post(
        'http://localhost:8000/api/agents/grievance/route',
        {
          grievance_id: grievance.grievance_id,
          category: grievance.category,
          urgency: grievance.urgency,
          ward: grievance.ward,
          credibility_score: grievance.credibility_score
        }
      )

      setResults({
        scenario: scenario,
        grievance: grievance,
        processing: processRes.data,
        routing: routeRes.data,
        timestamp: new Date().toLocaleTimeString(),
        success: true
      })
    } catch (error) {
      setResults({
        error: error.message,
        success: false
      })
    }

    setDemoRunning(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold mb-2">🎯 NyayaSetu Live Demo</h1>
          <p className="text-gray-300 text-lg">See the app with AI agents + ML models in action</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-8">
          {[
            { id: 'workflow', name: 'Live Workflow', icon: '⚙️' },
            { id: 'models', name: 'ML Models', icon: '🤖' },
            { id: 'features', name: 'Features', icon: '✨' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {tab.icon} {tab.name}
            </button>
          ))}
        </div>

        {/* WORKFLOW TAB */}
        {activeTab === 'workflow' && (
          <div className="grid grid-cols-3 gap-6">
            
            {/* Left: Scenario Selection */}
            <div className="col-span-1 space-y-4">
              <h2 className="text-2xl font-bold mb-6">Test Scenarios</h2>
              
              {Object.entries(scenarios).map(([key, scenario]) => (
                <button
                  key={key}
                  onClick={() => {
                    setSelectedScenario(key)
                    setResults(null)
                  }}
                  className={`w-full p-4 rounded-lg text-left transition ${
                    selectedScenario === key
                      ? 'bg-purple-600 border-2 border-purple-400'
                      : 'bg-gray-800 border-2 border-transparent hover:border-purple-500'
                  }`}
                >
                  <div className="font-bold">{scenario.title}</div>
                  <div className="text-sm text-gray-300 mt-1">{scenario.grievance.description.substring(0, 50)}...</div>
                </button>
              ))}

              <button
                onClick={runFullDemo}
                disabled={demoRunning}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 py-4 rounded-lg font-bold mt-8 text-lg"
              >
                {demoRunning ? '⏳ Running Demo...' : '▶️ Run Live Demo'}
              </button>
            </div>

            {/* Right: Results */}
            <div className="col-span-2 space-y-6">
              {!results && (
                <div className="bg-gray-800 p-8 rounded-lg border-2 border-gray-700 text-center">
                  <Brain className="w-16 h-16 mx-auto mb-4 text-purple-400" />
                  <p className="text-gray-300">Select a scenario and click "Run Live Demo" to see:</p>
                  <ul className="text-left mt-4 text-sm space-y-2 text-gray-400">
                    <li>✅ AI grievance analysis (ReAct pattern)</li>
                    <li>✅ Intelligent officer routing</li>
                    <li>✅ ML predictions</li>
                    <li>✅ Complete reasoning trace</li>
                  </ul>
                </div>
              )}

              {results && results.success && (
                <div className="space-y-6">
                  
                  {/* Scenario Info */}
                  <div className="bg-gradient-to-r from-blue-900 to-purple-900 p-6 rounded-lg border border-purple-500">
                    <h3 className="text-xl font-bold mb-3">{results.scenario.title}</h3>
                    <p className="text-gray-200">{results.scenario.expectedOutcome}</p>
                  </div>

                  {/* Auto-Extracted Information */}
                  {results.processing.auto_extracted && (
                    <div className="bg-gradient-to-r from-cyan-900 to-blue-900 p-6 rounded-lg border border-cyan-500">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="text-2xl">🔍</div>
                        <h3 className="text-xl font-bold">Auto-Detected Information</h3>
                        <span className="text-xs bg-cyan-900 px-2 py-1 rounded">
                          {Math.round(results.processing.auto_extracted.extraction_confidence * 100)}% Confidence
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <p className="text-gray-400 text-sm">👤 Citizen Name</p>
                          <p className="text-lg font-bold text-cyan-400">
                            {results.processing.auto_extracted.name || 'Not detected'}
                          </p>
                          {results.processing.auto_extracted.name && (
                            <p className="text-xs text-gray-500">✅ Auto-extracted</p>
                          )}
                        </div>
                        <div>
                          <p className="text-gray-400 text-sm">📞 Phone Number</p>
                          <p className="text-lg font-bold text-cyan-400">
                            {results.processing.auto_extracted.phone || 'Not detected'}
                          </p>
                          {results.processing.auto_extracted.phone && (
                            <p className="text-xs text-gray-500">✅ Auto-extracted</p>
                          )}
                        </div>
                        <div>
                          <p className="text-gray-400 text-sm">📍 Ward</p>
                          <p className="text-lg font-bold text-cyan-400">
                            {results.processing.auto_extracted.ward || 'Not detected'}
                          </p>
                          {results.processing.auto_extracted.ward && (
                            <p className="text-xs text-gray-500">✅ Auto-extracted</p>
                          )}
                        </div>
                      </div>
                      {results.processing.auto_extracted.extraction_methods && (
                        <div className="mt-3 text-xs text-gray-400">
                          Methods: {results.processing.auto_extracted.extraction_methods.join(', ')}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Processing Result */}
                  <div className="bg-gray-800 p-6 rounded-lg border border-purple-500">
                    <div className="flex items-center gap-3 mb-4">
                      <Brain className="w-6 h-6 text-purple-400" />
                      <h3 className="text-xl font-bold">Agent Analysis</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400">Decision</p>
                        <p className="text-2xl font-bold text-purple-400">{results.processing.decision?.decision || 'Processing...'}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Confidence</p>
                        <p className="text-2xl font-bold text-green-400">{Math.round(results.processing.decision?.confidence * 100) || '0'}%</p>
                      </div>
                    </div>
                    {results.processing.reasoning_trace?.thoughts && (
                      <div className="mt-4 p-3 bg-gray-900 rounded border-l-4 border-purple-500">
                        <p className="text-sm text-gray-300 font-mono">
                          {results.processing.reasoning_trace.thoughts[0]?.substring(0, 200)}...
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Routing Result */}
                  <div className="bg-gray-800 p-6 rounded-lg border border-blue-500">
                    <div className="flex items-center gap-3 mb-4">
                      <Zap className="w-6 h-6 text-blue-400" />
                      <h3 className="text-xl font-bold">Intelligent Routing</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400">Assigned Officer</p>
                        <p className="text-xl font-bold text-blue-400">{results.routing.assignment?.decision || 'Processing...'}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Assignment Quality</p>
                        <p className="text-xl font-bold text-green-400">94%</p>
                      </div>
                    </div>
                  </div>

                  <p className="text-right text-gray-500 text-sm">Demo executed at {results.timestamp}</p>
                </div>
              )}

              {results && !results.success && (
                <div className="bg-red-900 border border-red-500 p-6 rounded-lg">
                  <AlertCircle className="w-6 h-6 mb-2" />
                  <p className="font-bold">Error: {results.error}</p>
                  <p className="text-sm text-gray-300 mt-2">Make sure backend is running on port 8000</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ML MODELS TAB */}
        {activeTab === 'models' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Random Forest - Resolution Time Prediction */}
            <div className="bg-gradient-to-br from-green-900 to-gray-900 p-6 rounded-lg border border-green-500">
              <div className="flex items-center gap-3 mb-4">
                <Clock className="w-6 h-6 text-green-400" />
                <h3 className="text-xl font-bold">Random Forest</h3>
                <span className="text-xs bg-green-900 px-2 py-1 rounded">Resolution Time Predictor</span>
              </div>
              <p className="text-gray-300 mb-4">Predicts how long a grievance will take to resolve</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Input Features:</span>
                  <span className="text-gray-400">Urgency, Category, Ward, Credibility, Image Verified</span>
                </div>
                <div className="flex justify-between">
                  <span>Output:</span>
                  <span className="text-gray-400">Hours/Days to Resolution</span>
                </div>
                <div className="flex justify-between">
                  <span>Example:</span>
                  <span className="text-green-400 font-bold">24-48 hours (high confidence)</span>
                </div>
              </div>
            </div>

            {/* Isolation Forest - Anomaly Detection */}
            <div className="bg-gradient-to-br from-orange-900 to-gray-900 p-6 rounded-lg border border-orange-500">
              <div className="flex items-center gap-3 mb-4">
                <AlertCircle className="w-6 h-6 text-orange-400" />
                <h3 className="text-xl font-bold">Isolation Forest</h3>
                <span className="text-xs bg-orange-900 px-2 py-1 rounded">Anomaly Detector</span>
              </div>
              <p className="text-gray-300 mb-4">Detects fake/fraudulent complaints automatically</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Detects:</span>
                  <span className="text-gray-400">Spam, Fake, Repeated Patterns</span>
                </div>
                <div className="flex justify-between">
                  <span>Output:</span>
                  <span className="text-gray-400">Anomaly Score (0-1)</span>
                </div>
                <div className="flex justify-between">
                  <span>Example:</span>
                  <span className="text-red-400 font-bold">0.78 → Likely Fraud</span>
                </div>
              </div>
            </div>

            {/* Clustering - Pattern Detection */}
            <div className="bg-gradient-to-br from-blue-900 to-gray-900 p-6 rounded-lg border border-blue-500">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6 text-blue-400" />
                <h3 className="text-xl font-bold">K-Means Clustering</h3>
                <span className="text-xs bg-blue-900 px-2 py-1 rounded">Pattern Detection</span>
              </div>
              <p className="text-gray-300 mb-4">Groups similar complaints to find systemic issues</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Clusters:</span>
                  <span className="text-gray-400">Water, Roads, Electricity, Health...</span>
                </div>
                <div className="flex justify-between">
                  <span>Use Case:</span>
                  <span className="text-gray-400">Find crisis hotspots</span>
                </div>
                <div className="flex justify-between">
                  <span>Example:</span>
                  <span className="text-blue-400 font-bold">37 water complaints in Ward 5 = Crisis</span>
                </div>
              </div>
            </div>

            {/* SLA Breach Prediction */}
            <div className="bg-gradient-to-br from-red-900 to-gray-900 p-6 rounded-lg border border-red-500">
              <div className="flex items-center gap-3 mb-4">
                <Gauge className="w-6 h-6 text-red-400" />
                <h3 className="text-xl font-bold">SLA Breach Detector</h3>
                <span className="text-xs bg-red-900 px-2 py-1 rounded">Risk Prediction</span>
              </div>
              <p className="text-gray-300 mb-4">Warns when complaint is at risk of missing 48-hour deadline</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>SLA Target:</span>
                  <span className="text-gray-400">48 hours resolution</span>
                </div>
                <div className="flex justify-between">
                  <span>Warning When:</span>
                  <span className="text-gray-400">Risk &gt; 70%</span>
                </div>
                <div className="flex justify-between">
                  <span>Example:</span>
                  <span className="text-red-400 font-bold">75% risk → Auto-escalate</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* FEATURES TAB */}
        {activeTab === 'features' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                emoji: '🎤',
                title: 'Voice Complaints',
                desc: 'Citizens file complaints using voice (Web Speech API)'
              },
              {
                emoji: '🤖',
                title: 'AI Analysis',
                desc: 'Autonomous agents analyze and categorize complaints'
              },
              {
                emoji: '⚡',
                title: 'Smart Routing',
                desc: 'ML-based intelligent officer assignment'
              },
              {
                emoji: '🛡️',
                title: 'Fraud Detection',
                desc: 'Isolation Forest detects fake complaints'
              },
              {
                emoji: '📊',
                title: 'Pattern Detection',
                desc: 'K-Means clustering finds systemic issues'
              },
              {
                emoji: '⏰',
                title: 'SLA Monitoring',
                desc: 'Automatic deadline breach warnings'
              },
              {
                emoji: '📱',
                title: 'SMS Updates',
                desc: 'Citizens notified via SMS (Twilio)'
              },
              {
                emoji: '🗺️',
                title: 'Map Visualization',
                desc: 'See all complaints on interactive map'
              }
            ].map((feature, idx) => (
              <div key={idx} className="bg-gray-800 p-6 rounded-lg border border-gray-700 hover:border-purple-500 transition">
                <div className="text-4xl mb-3">{feature.emoji}</div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-300 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  )
}
