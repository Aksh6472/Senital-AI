'use client';

import React from 'react';
import { Camera, Incident, responderLocations } from '../../lib/mockData';
import { ShieldCheck, Video, AlertTriangle, Cpu, Radio, ShieldAlert } from 'lucide-react';

interface SOCDashboardProps {
  cameras: Camera[];
  incidents: Incident[];
  setActiveTab: (tab: string) => void;
  onSelectIncident: (incident: Incident) => void;
}

export function SOCDashboard({ cameras, incidents, setActiveTab, onSelectIncident }: SOCDashboardProps) {
  const onlineCameras = cameras.filter(c => c.status === 'online').length;
  const criticalPending = incidents.filter(i => i.status === 'pending' && i.severity === 'critical').length;
  const pendingTriageCount = incidents.filter(i => i.status === 'pending').length;

  return (
    <div className="flex flex-col gap-6 w-full font-mono">
      
      {/* HUD Telemetry Stats Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <div className="glass-panel p-5 rounded-xl border border-custom bg-blue-950/10 flex justify-between items-center">
          <div>
            <span className="text-[10px] text-blue-400 font-bold block mb-1">CAMERA NETWORK UPTIME</span>
            <span className="text-2xl font-bold text-white">{onlineCameras}/{cameras.length} ON</span>
          </div>
          <Video className="h-8 w-8 text-blue-500/50" />
        </div>

        <div className="glass-panel p-5 rounded-xl border border-custom bg-red-950/15 flex justify-between items-center animate-alert-pulse">
          <div>
            <span className="text-[10px] text-red-400 font-bold block mb-1">UNRESOLVED THREATS</span>
            <span className="text-2xl font-bold text-white">{criticalPending} CRITICAL</span>
          </div>
          <AlertTriangle className="h-8 w-8 text-red-500/50 animate-pulse" />
        </div>

        <div className="glass-panel p-5 rounded-xl border border-custom bg-yellow-950/10 flex justify-between items-center">
          <div>
            <span className="text-[10px] text-yellow-400 font-bold block mb-1">PENDING TRIAGE QUEUE</span>
            <span className="text-2xl font-bold text-white">{pendingTriageCount} INCIDENTS</span>
          </div>
          <ShieldAlert className="h-8 w-8 text-yellow-500/50" />
        </div>

        <div className="glass-panel p-5 rounded-xl border border-custom bg-green-950/10 flex justify-between items-center">
          <div>
            <span className="text-[10px] text-green-400 font-bold block mb-1">RESPONDERS PATROL</span>
            <span className="text-2xl font-bold text-white">{responderLocations.length} UNITS</span>
          </div>
          <ShieldCheck className="h-8 w-8 text-green-500/50" />
        </div>

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Core Live Threat Feed shortcut panel */}
        <div className="glass-panel p-5 rounded-xl border border-custom bg-black/10 flex flex-col justify-between lg:col-span-2">
          <div>
            <div className="flex justify-between items-center mb-4 border-b border-custom pb-3">
              <span className="text-xs font-bold text-white uppercase">CRITICAL SYSTEM THREAT FEEDS</span>
              <button 
                onClick={() => setActiveTab('incidents')}
                className="text-[10px] text-blue-400 hover:text-blue-300 font-bold uppercase transition-colors"
              >
                VIEW FULL FEED &rarr;
              </button>
            </div>

            <div className="space-y-3.5">
              {incidents.slice(0, 3).map((inc) => (
                <div 
                  key={inc.id}
                  onClick={() => onSelectIncident(inc)}
                  className={`p-3 rounded-lg border flex items-center justify-between cursor-pointer hover:bg-white/5 transition-all ${
                    inc.severity === 'critical' 
                      ? 'border-red-500/30 bg-red-950/5' 
                      : 'border-custom bg-black/25'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                        inc.severity === 'critical' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-orange-500/10 text-orange-400'
                      }`}>
                        {inc.severity.toUpperCase()}
                      </span>
                      <span className="text-xs font-bold text-gray-200">[{inc.id}] {inc.type}</span>
                    </div>
                    <p className="text-[11px] text-gray-400 mt-1">{inc.message}</p>
                  </div>
                  
                  <span className="text-[10px] text-gray-500 font-semibold">{inc.cameraName}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Live Camera overview list */}
        <div className="glass-panel p-5 rounded-xl border border-custom bg-black/10 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4 border-b border-custom pb-3">
              <span className="text-xs font-bold text-white uppercase">CAMERA TELEMETRY</span>
              <button 
                onClick={() => setActiveTab('cameras')}
                className="text-[10px] text-blue-400 hover:text-blue-300 font-bold uppercase transition-colors"
              >
                GRID VIEW &rarr;
              </button>
            </div>

            <div className="space-y-3">
              {cameras.map((cam) => (
                <div key={cam.id} className="flex justify-between items-center text-xs p-2 rounded bg-black/20 border border-custom">
                  <div className="flex items-center gap-2">
                    <span className={`h-1.5 w-1.5 rounded-full ${
                      cam.status === 'online' ? 'bg-green-500' :
                      cam.status === 'degraded' ? 'bg-yellow-500' :
                      'bg-red-500'
                    } animate-pulse`} />
                    <span className="text-gray-300">{cam.name}</span>
                  </div>
                  <span className="text-gray-500 text-[10px]">{cam.site}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
