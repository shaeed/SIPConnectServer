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

  // Devices
  getUserDevices: (username)             => request('GET',    `/sip/users/${username}/devices`),
  removeDevice:   (username, deviceId)   => request('DELETE', `/sip/client/${username}/${deviceId}`),

  // Config
  getConfig:    ()       => request('GET', '/api/config'),
  getTtyDevices: ()      => request('GET', '/api/tty-devices'),
  uploadSA:     (form)   => upload('/upload_sa', form),

  // Logs
  getCallLogs:  () => request('GET', '/api/logs/call'),
  getSmsLogs:   () => request('GET', '/api/logs/sms'),

  // Web Push
  getVapidPublicKey: ()   => request('GET',  '/api/vapid-public-key'),
  registerWebPush:   (data) => request('POST', '/sip/client/register/web-push', data),
}
