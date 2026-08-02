'use client';

import React from 'react';
import { Incident } from '../../lib/mockData';
import { BoundingBoxOverlay } from './BoundingBoxOverlay';
import { TimelineView } from './TimelineView';
import { Download, AlertCircle, Calendar, ShieldCheck, MapPin } from 'lucide-react';
import { api } from '../../lib/api';

interface EvidenceViewerProps {
  selectedIncident: Incident | null;
  onDownloadReport: (id: string) => void;
}

export function EvidenceViewer({ selectedIncident, onDownloadReport }: EvidenceViewerProps) {
  if (!selectedIncident) {
    return (
      <div className="glass-panel rounded-xl p-12 text-center text-gray-500 border border-custom flex flex-col items-center justify-center gap-3 h-[500px]">
        <AlertCircle className="h-10 w-10 text-gray-600 animate-pulse" />
        <span className="text-xs font-mono">SELECT AN INCIDENT FROM THE INCIDENT FEED OR DASHBOARD TO INVESTIGATE EVIDENCE</span>
      </div>
    );
  }

  const formattedDate = new Date(selectedIncident.timestamp).toLocaleString();

  return (
    <div className="flex flex-col xl:flex-row gap-6 w-full font-mono">
      
      {/* Visual Bounding Box Analyzer & Image Frame */}
      <div className="flex-1 flex flex-col gap-4">
        <div className="glass-panel rounded-xl overflow-hidden border border-custom bg-black">
          <div className="relative aspect-video w-full bg-slate-950 flex items-center justify-center">
            <div className="absolute inset-0 bg-[radial-gradient(#388bfd_1px,transparent_1px)] opacity-[0.03] [background-size:16px_16px] z-10" />
            <div className="scanner-overlay absolute inset-0 opacity-20 pointer-events-none" />

            {/* Display bounding box on frame */}
            {selectedIncident.evidence.map((evi) => (
              <BoundingBoxOverlay key={evi.id} evidence={evi} />
            ))}

            <div className="absolute top-4 left-4 z-20 bg-black/80 border border-custom px-3 py-1 rounded text-[10px] text-gray-400">
              FRAME SNAPSHOT | TIMESTAMP: {formattedDate}
            </div>

            {/* Crosshair indicator */}
            <div className="absolute inset-x-0 top-1/2 border-t border-white/5 pointer-events-none" />
            <div className="absolute inset-y-0 left-1/2 border-l border-white/5 pointer-events-none" />

            <div className="text-[10px] text-gray-600 tracking-wider">EVIDENCE SOURCE: {selectedIncident.cameraName}</div>
          </div>
        </div>

        {/* AI Explanatory Description block */}
        <div className="glass-panel p-5 rounded-xl border border-custom bg-black/10 space-y-3">
          <div className="flex items-center gap-2 text-blue-400 text-xs font-bold">
            <ShieldCheck className="h-4.5 w-4.5" />
            <span>AI PIPELINE INTERPRETATION & EXPLANATION</span>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed bg-black/30 p-3 rounded-lg border border-custom">
            {selectedIncident.explanation}
          </p>
        </div>
      </div>

      {/* Audit Log / Timeline & Actions Sidebar */}
      <div className="w-full xl:w-96 flex flex-col gap-6">
        
        {/* Incident Summary Metadata */}
        <div className="glass-panel p-5 rounded-xl border border-custom bg-black/10 space-y-4">
          <div className="flex justify-between items-start gap-4">
            <div>
              <span className="text-[10px] text-gray-500 font-bold block mb-1">INCIDENT KEY</span>
              <h3 className="text-sm font-bold text-white">{selectedIncident.id}</h3>
            </div>
            
            <button
              onClick={() => onDownloadReport(selectedIncident.id)}
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white font-bold px-3 py-2 rounded text-xs transition-colors cursor-pointer"
            >
              <Download className="h-3.5 w-3.5" />
              <span>EXPORT PDF</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4 border-t border-custom pt-4 text-[11px]">
            <div>
              <span className="text-[9px] text-gray-500 block mb-0.5">SEVERITY LEVEL</span>
              <span className="text-white uppercase font-bold">{selectedIncident.severity}</span>
            </div>
            <div>
              <span className="text-[9px] text-gray-500 block mb-0.5">RESOLUTION STATUS</span>
              <span className="text-white uppercase font-bold">{selectedIncident.status}</span>
            </div>
            <div>
              <span className="text-[9px] text-gray-500 block mb-0.5">CAMERA SOURCE</span>
              <span className="text-white font-bold">{selectedIncident.cameraName}</span>
            </div>
            <div>
              <span className="text-[9px] text-gray-500 block mb-0.5">GPS COORDINATES</span>
              <span className="text-white font-bold">{selectedIncident.location.lat.toFixed(4)}, {selectedIncident.location.lng.toFixed(4)}</span>
            </div>
          </div>
        </div>

        {/* Sequential Timeline Audit Trail */}
        <div className="glass-panel p-5 rounded-xl border border-custom flex-1 bg-black/10 flex flex-col justify-between">
          <div>
            <span className="text-[10px] text-gray-500 font-bold block mb-4">TRIAGE EVENT TIMELINE</span>
            <TimelineView timeline={selectedIncident.timeline} />
          </div>
        </div>

      </div>

    </div>
  );
}
