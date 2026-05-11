async function request(method, path, body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(path, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

async function upload(path, formData) {
  const res = await fetch(path, { method: 'POST', body: formData })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
}

export const api = {
  // Users
  getUsers:     ()               => request('GET',    '/sip/users'),
  getUser:      (username)       => request('GET',    `/sip/users/${username}`),
  createUser:   (data)           => request('POST',   '/sip/users', data),
  updateUser:   (username, data) => request('PUT',    `/sip/users/${username}`, data),
  deleteUser:   (username)       => request('DELETE', `/sip/users/${username}`),

  // Config
  getConfig:    ()       => request('GET', '/api/config'),
  uploadSA:     (form)   => upload('/upload_sa', form),
  downloadDB:   ()       => { window.location.href = '/sip/db' },
  uploadDB:     (form)   => upload('/sip/db', form),

  // Logs
  getCallLogs:  () => request('GET', '/api/logs/call'),
  getSmsLogs:   () => request('GET', '/api/logs/sms'),
}
