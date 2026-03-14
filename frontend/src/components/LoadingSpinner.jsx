import React from "react";

export default function LoadingSpinner({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      {/* Spinning ring */}
      <div className="h-12 w-12 rounded-full border-4 border-gray-200 border-t-accent animate-spin" />

      {message && (
        <p className="mt-4 text-sm text-gray-500 font-body">{message}</p>
      )}
    </div>
  );
}
