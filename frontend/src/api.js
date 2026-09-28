const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')

// The backend currently inserts the question into a JSON string template
// without escaping, so newlines, double quotes and backslashes cause a 500.
// Normalize them here; remove once the backend serializes the body properly.
function toBackendSafe(question) {
  return question
    .replace(/[\u0000-\u001f\u007f]+/g, ' ')
    .replace(/"/g, "'")
    .replace(/\\/g, '/')
    .replace(/\s{2,}/g, ' ')
    .trim()
}

export async function askQuestion(question, signal) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}/api/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: toBackendSafe(question) }),
      signal,
    })
  } catch (err) {
    if (err.name === 'AbortError') throw err
    throw new Error('Could not reach the server. Please check that the backend is running.')
  }

  if (!response.ok) {
    throw new Error(`The server could not answer this question (HTTP ${response.status}). Please try again.`)
  }

  const data = await response.json().catch(() => null)
  if (!data || typeof data.answer !== 'string' || !data.answer.trim()) {
    throw new Error('The server returned an empty or unexpected response.')
  }
  return data.answer
}

export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, { cache: 'no-store' })
    return response.ok
  } catch {
    return false
  }
}
