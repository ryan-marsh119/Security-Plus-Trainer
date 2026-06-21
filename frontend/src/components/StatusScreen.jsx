/**
 * components/StatusScreen.jsx
 *
 * Centered full-height status message used by the session pages for loading and
 * error states. When `onRetry` is provided it renders a retry button — this is
 * what keeps a failed API call from stranding the user on an infinite spinner.
 *
 * Props:
 *   message    {string}   -- text to show
 *   onRetry    {function} -- optional; renders a retry button when present
 *   retryLabel {string}   -- button label (default: "Try Again")
 *   tone       {'muted'|'error'} -- styling (default: 'muted')
 */
export default function StatusScreen({ message, onRetry, retryLabel = 'Try Again', tone = 'muted' }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="text-center">
        <p className={tone === 'error' ? 'text-red-600' : 'text-gray-500'}>{message}</p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 bg-blue-600 text-white rounded-xl px-6 py-2 font-semibold hover:bg-blue-700"
          >
            {retryLabel}
          </button>
        )}
      </div>
    </div>
  )
}
