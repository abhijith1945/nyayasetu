import React from "react";

export default function ErrorCard({ message, onRetry }) {
  return (
    <div className="mx-auto max-w-md rounded-lg border border-red-200 bg-red-50 p-6 text-center shadow-sm">
      {/* Error icon */}
      <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-2xl">
        !
      </div>

      <h3 className="mb-1 font-heading text-lg font-semibold text-red-700">
        Something went wrong
      </h3>

      <p className="mb-4 font-body text-sm text-red-600">
        {message || "An unexpected error occurred. Please try again."}
      </p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Retry
        </button>
      )}
    </div>
  );
}
