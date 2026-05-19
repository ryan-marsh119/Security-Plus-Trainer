/**
 * api/client.js
 *
 * Pre-configured Axios instance used by all API calls in the app.
 *
 * Base URL: /api/v1  (proxied to http://localhost:8000 in dev via vite.config.js)
 * Auth:     Django session cookie — automatically sent with every request because
 *           withCredentials is true.
 * CSRF:     Django requires an X-CSRFToken header on all state-changing requests
 *           (POST, PUT, PATCH, DELETE). The request interceptor below reads the
 *           csrftoken cookie that Django sets and attaches it as a header.
 *           React never stores the token in JS state — it reads from the cookie
 *           at request time to stay in sync with the server.
 */

import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  withCredentials: true, // send session cookie cross-origin in dev
})

/**
 * Request interceptor — attaches the CSRF token to mutating requests.
 *
 * Django's CsrfViewMiddleware rejects POST/PUT/PATCH/DELETE requests that
 * lack a matching X-CSRFToken header. The token value is read from the
 * csrftoken cookie which Django sets on the first page load or admin visit.
 */
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
