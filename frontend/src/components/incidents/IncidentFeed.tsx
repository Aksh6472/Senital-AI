'use client';

import React, { useState } from 'react';
import { Incident } from '../../lib/mockData';
import { IncidentCard } from './IncidentCard';
import { ShieldAlert, RefreshCw } from 'lucide-react';

interface IncidentFeedProps {
  incidents: Incident[];
  onConfirm: (id: string) => void;
  onDismiss: (id: string) => void;
  onEscalate: (id: string) => void;
  onSelectIncident: (incident: Incident) => void;
}

export function IncidentFeed({ 
  incidents, 
  onConfirm, 
  onDismiss, 
  onEscalate, 
  onSelectIncident 
}: IncidentFeedProps) {
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredIncidents = incidents.filter(inc => {
    const severityMatch = severityFilter === 'all' || inc.severity === severityFilter;
    const statusMatch = statusFilter === 'all' || inc.status === statusFilter;
    return severityMatch && statusMatch;
  });

  return (
    <div className="flex flex-col gap-6 w-full font-mono">
      
      {/* Triage filters header */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-black/30 p-4 rounded-xl border border-custom glass-panel">
        <div className="flex items-center gap-4">
          <div>
            <label className="block text-[10px] text-gray-400 mb-1">SEVERITY LEVEL</label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-black/50 border border-custom rounded px-3 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-blue-500/50"
            >
              <option value="all">ALL SEVERITIES</option>
              <option value="critical">CRITICAL ONLY</option>
              <option value="high">HIGH & ABOVE</option>
              <option value="medium">MEDIUM</option>
              <option value="low">LOW</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-gray-400 mb-1">TRIAGE STATUS</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-black/50 border border-custom rounded px-3 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-blue-500/50"
            >
              <option value="all">ALL STATUSES</option>
              <option value="pending">PENDING TRIAGE</option>
              <option value="confirmed">CONFIRMED</option>
              <option value="dismissed">DISMISSED</option>
              <option value="escalated">ESCALATED</option>
            </select>
          </div>
        </div>

        <div className="text-[10px] text-gray-400 flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
          <span>REAL-TIME PIPELINE STREAMING</span>
        </div>
      </div>

      {/* Incident Stream Card List */}
      <div className="flex flex-col gap-4">
        {filteredIncidents.length === 0 ? (
          <div className="glass-panel rounded-xl p-12 text-center text-gray-500 border border-custom flex flex-col items-center gap-3">
            <ShieldAlert className="h-10 w-10 text-gray-600 animate-pulse" />
            <span className="text-xs">No matching incidents in current triage queue</span>
          </div>
        ) : (
          filteredIncidents.map((incident) => (
            <IncidentCard
              key={incident.id}
              incident={incident}
              onConfirm={onConfirm}
              onDismiss={onDismiss}
              onEscalate={onEscalate}
              onSelect={onSelectIncident}
            />
          ))
        )}
      </div>

    </div>
  );
}
