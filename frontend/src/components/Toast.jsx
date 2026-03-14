import React, { useState, useEffect, useRef } from "react";

const TYPE_STYLES = {
  success: "bg-accent text-white",
  error: "bg-critical text-white",
  info: "bg-blue-500 text-white",
};

const TYPE_ICONS = {
  success: "\u2713",
  error: "\u2717",
  info: "\u24D8",
};

export default function Toast({ message, type = "info", onClose }) {
  const [exiting, setExiting] = useState(false);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  useEffect(() => {
    const dismissTimer = setTimeout(() => {
      setExiting(true);
    }, 2700);

    const removeTimer = setTimeout(() => {
      onCloseRef.current?.();
    }, 3000);

    return () => {
      clearTimeout(dismissTimer);
      clearTimeout(removeTimer);
    };
  }, []);

  const colorClass = TYPE_STYLES[type] || TYPE_STYLES.info;
  const icon = TYPE_ICONS[type] || TYPE_ICONS.info;

  return (
    <div
      className={`fixed top-4 right-4 z-50 flex max-w-sm items-center gap-3 rounded-lg px-5 py-3 shadow-lg font-body text-sm ${colorClass} ${
        exiting ? "toast-exit" : "toast-enter"
      }`}
      role="alert"
    >
      <span className="text-lg leading-none">{icon}</span>
      <span className="flex-1">{message || ""}</span>
      <button
        onClick={() => onClose?.()}
        className="ml-2 text-lg leading-none opacity-80 hover:opacity-100 focus:outline-none"
        aria-label="Close notification"
      >
        &times;
      </button>
    </div>
  );
}
