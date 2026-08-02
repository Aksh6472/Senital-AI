'use client';

import React from 'react';
import { Incident } from '../../lib/mockData';
import { ShieldCheck, ShieldAlert, Ban, Siren, Search, Clock } from 'lucide-react';

interface IncidentCardProps {
  incident: Incident;
  onConfirm: (id: string) => void;
  onDismiss: (id: string) => void;
  onEscalate: (id: string) => void;
  onSelect: (incident: Incident) => void;
}

export function IncidentCard({ 
  incident, 
  onConfirm, 
  onDismiss, 
  onEscalate, 
  onSelect 
}: IncidentCardProps) {

  const severityColors = {
    critical: 'bg-red-500/10 text-red-400 border border-red-500/30',
    high: 'bg-orange-500/10 text-orange-400 border border-orange-500/30',
    medium: 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30',
    low: 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
  };

  const statusColors = {
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40',
    confirmed: 'bg-green-500/20 text-green-400 border-green-500/40',
    dismissed: 'bg-gray-800 text-gray-500 border-gray-700',
    escalated: 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse'
  };

  const formattedTime = new Date(incident.timestamp).toLocaleTimeString();
  const isCriticalPending = incident.severity === 'critical' && incident.status === 'pending';

  return (
    <div className={`glass-panel rounded-xl overflow-hidden border transition-all duration-300 flex flex-col lg:flex-row justify-between ${
      isCriticalPending 
        ? 'border-red-500/60 shadow-[0_0_15px_rgba(239,68,68,0.15)] animate-alert-pulse' 
        : 'border-custom'
    }`}>
      
      {/* Visual Header / Summary block */}
      <div className="p-5 flex-1 flex flex-col justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${severityColors[incident.severity]}`}>
            {incident.severity.toUpperCase()}
          </span>
          <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${statusColors[incident.status]}`}>
            {incident.status.toUpperCase()}
          </span>
          
          <div className="flex items-center gap-1.5 text-gray-400 text-xs ml-auto">
            <Clock className="h-3.5 w-3.5" />
            <span>{formattedTime}</span>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-bold text-gray-100 flex items-center gap-2">
            <span className="text-blue-400">[{incident.id}]</span> {incident.type}
          </h4>
          <p className="text-xs text-gray-300 mt-1">{incident.message}</p>
          <span className="text-[10px] text-gray-500 mt-2 block font-semibold">
            CAMERA ORIGIN: {incident.cameraName} ({incident.cameraId})
          </span>
        </div>
      </div>

      {/* Operator controls sidebar */}
      <div className="border-t lg:border-t-0 lg:border-l border-custom p-4 bg-black/10 flex flex-row lg:flex-col justify-center items-stretch gap-2 min-w-[180px]">
        {incident.status === 'pending' ? (
          <>
            <button
              onClick={() => onConfirm(incident.id)}
              className="flex-1 flex items-center justify-center gap-1.5 bg-green-700/20 hover:bg-green-600/35 border border-green-500/40 text-green-400 font-bold px-3 py-2 rounded text-xs transition-colors cursor-pointer"
            >
              <ShieldCheck className="h-4 w-4" />
              <span>CONFIRM</span>
            </button>
            <button
              onClick={() => onDismiss(incident.id)}
              className="flex-1 flex items-center justify-center gap-1.5 bg-gray-900 hover:bg-gray-800 border border-gray-700 text-gray-400 font-bold px-3 py-2 rounded text-xs transition-colors cursor-pointer"
            >
              <Ban className="h-4 w-4" />
              <span>DISMISS</span>
            </button>
            <button
              onClick={() => onEscalate(incident.id)}
              className="flex-1 flex items-center justify-center gap-1.5 bg-red-950/30 hover:bg-red-900/45 border border-red-500/40 text-red-400 font-bold px-3 py-2 rounded text-xs transition-colors cursor-pointer"
            >
              <Siren className="h-4 w-4 animate-pulse" />
              <span>ESCALATE</span>
            </button>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-center py-2 text-[10px] text-gray-500 italic uppercase">
            Resolved / Triage Complete
          </div>
        )}

        <button
          onClick={() => onSelect(incident)}
          className="flex-1 flex items-center justify-center gap-1.5 bg-blue-600/10 hover:bg-blue-600/20 border border-blue-500/30 text-blue-400 font-semibold px-3 py-2 rounded text-xs transition-colors cursor-pointer"
        >
          <Search className="h-4 w-4" />
          <span>INVESTIGATE</span>
        </button>
      </div>

    </div>
  );
}
