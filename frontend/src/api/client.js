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
/**
 * Reads a cookie value by name. Regex-based so it tolerates leading spaces and
 * is robust to the cookie not being the first in the string. Returns null if
 * the cookie is absent.
 */
function readCookie(name) {
  const match = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'))
  return match ? decodeURIComponent(match[1]) : null
}

client.interceptors.request.use((config) => {
  if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
    const csrfToken = readCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }
  return config
})

/**
 * Response interceptor — central place for cross-cutting error handling.
 *
 * If the session expires mid-app, the server returns 401/403 on a protected
 * call. We bounce the user to /login so they re-authenticate, EXCEPT for the
 * auth endpoints themselves (a 401 from /auth/login/ is "bad credentials" and
 * a 403 from /auth/me/ is the normal "no session yet" probe — both are handled
 * by their callers). Errors are otherwise passed through unchanged so component
 * try/catch and the store error states still see them.
 */
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const url = error?.config?.url ?? ''
    const isAuthEndpoint = url.includes('/auth/')
    if ((status === 401 || status === 403) && !isAuthEndpoint) {
      if (window.location.pathname !== '/login') {
        window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  },
)

export default client
