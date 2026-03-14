import React from "react";
import { QRCodeSVG } from "qrcode.react";
import UrgencyBadge from "./UrgencyBadge";

export default function ReceiptCard({ grievance, onTrack }) {
  const id = grievance?.id || "";
  const hash = grievance?.hash || "";
  const category = grievance?.category || "General";
  const urgency = grievance?.urgency ?? 1;

  const shortId = id.length > 8 ? id.slice(0, 8) : id;

  const whatsappText = encodeURIComponent(
    `NyayaSetu Grievance Receipt\nID: ${shortId}\nHash: ${hash}\nTrack: ${window.location.origin}/track/${id}`
  );

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

      {/* QR Code */}
      <div className="mx-auto mb-2 flex justify-center">
        <QRCodeSVG
          value={JSON.stringify({ id: shortId, hash, url: `${window.location.origin}/track/${id}` })}
          size={120}
          level="M"
          bgColor="#ffffff"
          fgColor="#0F172A"
        />
      </div>
      <p className="mb-4 text-center text-xs text-gray-400 font-body">Scan to verify your complaint</p>

      {/* Details list */}
      <dl className="space-y-3 font-body text-sm">
        <div className="flex items-start justify-between gap-2">
          <dt className="text-gray-500">Grievance ID</dt>
          <dd className="font-mono font-semibold text-navy">{shortId || "--"}</dd>
        </div>

        <div className="flex flex-col gap-1">
          <dt className="text-gray-500">Tamper-proof receipt</dt>
          <dd className="break-all rounded bg-gray-50 px-2 py-1 font-mono text-xs text-gray-600">
            {hash || "N/A"}
          </dd>
        </div>

        <div className="flex items-center justify-between gap-2">
          <dt className="text-gray-500">Category</dt>
          <dd>
            <span className="inline-block rounded-full bg-navy/10 px-2.5 py-0.5 text-xs font-semibold text-navy">
              {category}
            </span>
          </dd>
        </div>

        <div className="flex items-center justify-between gap-2">
          <dt className="text-gray-500">Urgency</dt>
          <dd>
            <UrgencyBadge level={urgency} />
          </dd>
        </div>
      </dl>

      {/* Share + Download buttons */}
      <div className="mt-5 flex gap-2">
        <a
          href={`https://wa.me/?text=${whatsappText}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-green-500 px-3 py-2 text-sm font-semibold text-white transition-colors hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-1"
        >
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.5.5 0 00.611.611l4.458-1.495A11.953 11.953 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-2.325 0-4.478-.736-6.24-1.989l-.436-.318-2.93.982.982-2.93-.318-.436A9.953 9.953 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
          Share
        </a>
        <button
          onClick={() => window.print()}
          className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-navy px-3 py-2 text-sm font-semibold text-white transition-colors hover:bg-navy/90 focus:outline-none focus:ring-2 focus:ring-navy focus:ring-offset-1"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          Download
        </button>
      </div>

      {/* Track button */}
      {onTrack && (
        <button
          onClick={() => onTrack(id)}
          className="mt-3 w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
        >
          Track your complaint
        </button>
      )}
    </div>
  );
}
