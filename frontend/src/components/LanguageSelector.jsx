import React from 'react'
import './LanguageSelector.css'

const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
  { code: 'es', name: 'Español', flag: '🇪🇸' }
]

function LanguageSelector({ language, onLanguageChange }) {
  return (
    <div className="language-selector">
      <label>Language: </label>
      <select 
        value={language} 
        onChange={(e) => onLanguageChange(e.target.value)}
        className="language-select"
      >
        {LANGUAGES.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  )
}

export default LanguageSelector

