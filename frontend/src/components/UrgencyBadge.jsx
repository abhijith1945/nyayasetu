import React from "react";

const LEVEL_STYLES = {
  1: "bg-gray-100 text-gray-700",
  2: "bg-blue-100 text-blue-700",
  3: "bg-yellow-100 text-yellow-800",
  4: "bg-orange-100 text-orange-700",
  5: "bg-red-100 text-red-700",
};

export default function UrgencyBadge({ level }) {
  const safeLevel = Number(level) || 1;
  const clamped = Math.max(1, Math.min(5, safeLevel));
  const style = LEVEL_STYLES[clamped] || LEVEL_STYLES[1];

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold font-body ${style}`}
    >
      Urgency {clamped}
    </span>
  );
}
