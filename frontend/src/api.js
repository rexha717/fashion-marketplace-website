const BASE = '/api/auth'

const TOKEN_KEY = 'vellure.auth.token'

export function getToken() {
  try {
    return window.localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token) {
  try {
    if (token) window.localStorage.setItem(TOKEN_KEY, token)
    else window.localStorage.removeItem(TOKEN_KEY)
  } catch {
    /* storage unavailable (private mode) - session cookie still works */
  }
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Token ${token}` } : {}
}

/**
 * Flattens DRF error payloads into { field: [messages] } and always returns
 * a plain object so screens can render errors without special-casing.
 */
function normalizeErrors(data) {
  if (!data || typeof data !== 'object') return { nonFieldErrors: ['Something went wrong. Please try again.'] }
  const out = {}
  for (const [key, value] of Object.entries(data)) {
    if (key === 'detail') {
      out.nonFieldErrors = [value]
    } else if (Array.isArray(value)) {
      out[key] = value.map((v) => (typeof v === 'string' ? v : JSON.stringify(v)))
    }
  }
  if (!Object.keys(out).length) out.nonFieldErrors = ['Something went wrong. Please try again.']
  return out
}

async function request(path, { method = 'GET', body } = {}) {
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...authHeaders(),
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (response.status === 204) return null

  const text = await response.text()
  let data = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = { nonFieldErrors: ['Unexpected response from the server.'] }
    }
  }

  if (!response.ok) {
    const error = new Error('Request failed')
    error.fields = normalizeErrors(data)
    error.status = response.status
    throw error
  }

  return data
}

export async function signin({ username, password }) {
  const data = await request('/signin/', { method: 'POST', body: { username, password } })
  setToken(data.token)
  return data.user
}

export async function signup({ username, email, password, confirm_password: confirmPassword }) {
  const data = await request('/signup/', {
    method: 'POST',
    body: { username, email, password, confirm_password: confirmPassword },
  })
  setToken(data.token)
  return data.user
}

export async function logout() {
  try {
    await request('/logout/', { method: 'POST' })
  } finally {
    setToken(null)
  }
}

export async function me() {
  return request('/me/')
}
