/**
 * components/ErrorBoundary.jsx
 *
 * App-level React error boundary. Without it, a render-time throw anywhere in
 * the tree unmounts the whole app and leaves the user on a blank white screen.
 * This catches it and shows a recoverable fallback. Error boundaries must be
 * class components (no hook equivalent for componentDidCatch).
 */
import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    // Surface to the console for debugging; a real deployment could ship this
    // to an error-tracking service here.
    console.error('Unhandled UI error:', error, info)
  }

  handleReload = () => {
    this.setState({ hasError: false })
    window.location.assign('/dashboard')
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
          <div className="text-center">
            <p className="text-xl font-semibold text-gray-800">Something went wrong.</p>
            <p className="text-gray-500 mt-2">An unexpected error occurred while rendering this page.</p>
            <button
              type="button"
              onClick={this.handleReload}
              className="mt-6 bg-blue-600 text-white rounded-xl px-6 py-3 font-semibold hover:bg-blue-700"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
