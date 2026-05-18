import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
})

// Attach CSRF token from cookie to mutating requests
client.interceptors.request.use((config) => {
  if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
    const csrfToken = document.cookie
      .split('; ')
      .find((row) => row.startsWith('csrftoken='))
      ?.split('=')[1]
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }
  return config
})

export default client
