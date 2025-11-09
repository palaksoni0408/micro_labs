import React, { useState } from 'react'
import './MessageInput.css'

function MessageInput({ onSendMessage, disabled, placeholder }) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message)
      setMessage('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form className="message-input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className="message-input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={disabled}
      />
      <button 
        type="submit" 
        className="send-button"
        disabled={disabled || !message.trim()}
      >
        Send
      </button>
    </form>
  )
}

export default MessageInput

