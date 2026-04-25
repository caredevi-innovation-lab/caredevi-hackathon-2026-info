const API_BASE = 'http://localhost:8000/api'

export async function registerUser({ username, email, role, password, password_confirm }) {
  const res = await fetch(`${API_BASE}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, role, password, password_confirm }),
  })

  const data = await res.json()

  if (!res.ok) {
    const message =
      typeof data === 'object'
        ? Object.values(data).flat().join(' ')
        : 'Registration failed'
    throw new Error(message)
  }

  return data
}

export async function loginUser({ email, password }) {
  const res = await fetch(`${API_BASE}/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })


  const data = await res.json()

  if (!res.ok) {
    const message =
      typeof data === 'object'
        ? Object.values(data).flat().join(' ')
        : 'Login failed'
    throw new Error(message)
  }

  return data
}
