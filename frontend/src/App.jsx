import { useEffect, useRef, useState } from 'react'
import Markdown from 'react-markdown'
import { askQuestion, checkHealth } from './api.js'

const HEALTH_INTERVAL_MS = 30000

function StatusIndicator() {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    let active = true
    const run = async () => {
      const ok = await checkHealth()
      if (active) setStatus(ok ? 'online' : 'offline')
    }
    run()
    const id = setInterval(run, HEALTH_INTERVAL_MS)
    return () => {
      active = false
      clearInterval(id)
    }
  }, [])

  const label = { checking: 'Checking…', online: 'Online', offline: 'Offline' }[status]
  return (
    <div className={`status status-${status}`} title="Backend status">
      <span className="status-dot" aria-hidden="true" />
      {label}
    </div>
  )
}

function Message({ message }) {
  if (message.role === 'user') {
    return (
      <div className="message message-user">
        <div className="bubble">{message.content}</div>
      </div>
    )
  }
  if (message.role === 'error') {
    return (
      <div className="message message-assistant">
        <div className="bubble bubble-error" role="alert">{message.content}</div>
      </div>
    )
  }
  return (
    <div className="message message-assistant">
      <div className="bubble markdown">
        <Markdown>{message.content}</Markdown>
      </div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, loading])

  const send = async () => {
    const question = input.trim()
    if (!question || loading) return

    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', content: question }])
    setInput('')
    setLoading(true)

    try {
      const answer = await askQuestion(question)
      setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'assistant', content: answer }])
    } catch (err) {
      setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'error', content: err.message }])
    } finally {
      setLoading(false)
      textareaRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      send()
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    send()
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Spring Boot RAG Assistant</h1>
          <p className="subtitle">Ask questions about Spring Boot</p>
        </div>
        <StatusIndicator />
      </header>

      <main className="chat" aria-live="polite">
        {messages.length === 0 && !loading && (
          <div className="empty">
            <p>Ask anything about Spring Boot, such as configuration, auto-configuration, dependency injection, or Actuator.</p>
          </div>
        )}
        {messages.map((m) => (
          <Message key={m.id} message={m} />
        ))}
        {loading && (
          <div className="message message-assistant">
            <div className="bubble thinking">Thinking…</div>
          </div>
        )}
        <div ref={endRef} />
      </main>

      <form className="composer" onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about Spring Boot…"
          rows={3}
          aria-label="Your question"
          autoFocus
        />
        <div className="composer-footer">
          <span className="hint">Enter to send · Shift + Enter for a new line</span>
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? 'Sending…' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  )
}
