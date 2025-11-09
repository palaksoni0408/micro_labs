import React, { useState, useEffect, useRef } from 'react'
import ChatBot from './components/ChatBot'
import Disclaimer from './components/Disclaimer'
import LanguageSelector from './components/LanguageSelector'
import './App.css'

function App() {
  const [language, setLanguage] = useState('en')
  const [showDisclaimer, setShowDisclaimer] = useState(true)

  useEffect(() => {
    // Show disclaimer only on first load
    const disclaimerShown = localStorage.getItem('disclaimerShown')
    if (disclaimerShown) {
      setShowDisclaimer(false)
    }
  }, [])

  const handleDisclaimerAccept = () => {
    setShowDisclaimer(false)
    localStorage.setItem('disclaimerShown', 'true')
  }

  return (
    <div className="App">
      <div className="app-container">
        <header className="app-header">
          <h1>🌡️ HealthGuide</h1>
          <p className="subtitle">Fever Helpline - Your AI Health Assistant</p>
          <LanguageSelector language={language} onLanguageChange={setLanguage} />
        </header>

        {showDisclaimer && (
          <Disclaimer onAccept={handleDisclaimerAccept} language={language} />
        )}

        <ChatBot language={language} />
      </div>
    </div>
  )
}

export default App

