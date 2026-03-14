import React from "react";
import UrgencyBadge from "./UrgencyBadge";

export default function ReceiptCard({ grievance, onTrack }) {
  const id = grievance?.id || "";
  const hash = grievance?.hash || "";
  const category = grievance?.category || "General";
  const urgency = grievance?.urgency ?? 1;

  const shortId = id.length > 8 ? id.slice(0, 8) : id;

  return (
    <div className="mx-auto max-w-md rounded-xl border border-green-200 bg-white p-6 shadow-md">
      {/* Green checkmark */}
      <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-accent/10">
        <svg
          className="h-9 w-9 text-accent"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>

      <h3 className="mb-4 text-center font-heading text-lg font-bold text-navy">
        Grievance Submitted
      </h3>

      {/* Details list */}
      <dl className="space-y-3 font-body text-sm">
        {/* Grievance ID */}
        <div className="flex items-start justify-between gap-2">
          <dt className="text-gray-500">Grievance ID</dt>
          <dd className="font-mono font-semibold text-navy">{shortId || "--"}</dd>
        </div>

        {/* Tamper-proof receipt */}
        <div className="flex flex-col gap-1">
          <dt className="text-gray-500">Tamper-proof receipt</dt>
          <dd className="break-all rounded bg-gray-50 px-2 py-1 font-mono text-xs text-gray-600">
            {hash || "N/A"}
          </dd>
        </div>

        {/* Category */}
        <div className="flex items-center justify-between gap-2">
          <dt className="text-gray-500">Category</dt>
          <dd>
            <span className="inline-block rounded-full bg-navy/10 px-2.5 py-0.5 text-xs font-semibold text-navy">
              {category}
            </span>
          </dd>
        </div>

        {/* Urgency */}
        <div className="flex items-center justify-between gap-2">
          <dt className="text-gray-500">Urgency</dt>
          <dd>
            <UrgencyBadge level={urgency} />
          </dd>
        </div>
      </dl>

      {/* Track button */}
      {onTrack && (
        <button
          onClick={() => onTrack(id)}
          className="mt-6 w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
        >
          Track your complaint
        </button>
      )}
    </div>
  );
}
