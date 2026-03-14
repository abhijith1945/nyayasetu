import React from "react";

export default function StatCard({ title, value, icon, color }) {
  const borderColor = color || "border-accent";

  return (
    <div
      className={`flex items-center gap-4 rounded-lg border-l-4 ${borderColor} bg-white p-5 shadow-sm`}
    >
      {/* Icon */}
      {icon && (
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gray-100 text-2xl">
          {icon}
        </span>
      )}

      {/* Text */}
      <div className="min-w-0">
        <p className="truncate text-sm font-body text-gray-500">
          {title || "Stat"}
        </p>
        <p className="text-2xl font-heading font-bold text-navy">
          {value ?? "--"}
        </p>
      </div>
    </div>
  );
}
