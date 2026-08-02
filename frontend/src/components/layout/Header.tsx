'use client';

import React from 'react';
import { Shield, Radio, Activity, AlertTriangle } from 'lucide-react';

interface HeaderProps {
  isConnected: boolean;
  activeDetections: number;
  criticalAlertCount: number;
}

export function Header({ isConnected, activeDetections, criticalAlertCount }: HeaderProps) {
  return (
    <header className="h-16 border-b border-custom glass-panel flex items-center justify-between px-6 z-30 sticky top-0">
      <div className="flex items-center gap-3">
        <div className="bg-blue-600/10 p-2 rounded-lg border border-blue-500/30">
          <Shield className="h-6 w-6 text-blue-400" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-wider text-white">SENTINEL AI</h1>
          <p className="text-[10px] text-gray-400 font-mono tracking-widest">TACTICAL COMMAND OPERATIONS</p>
        </div>
      </div>

      <div className="flex items-center gap-6 font-mono text-xs">
        {/* Real-time backend connection status */}
        <div className="flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-md border border-custom">
          <span className={`h-2.5 w-2.5 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="text-gray-300">SYSTEM: {isConnected ? 'ONLINE' : 'OFFLINE'}</span>
        </div>

        {/* Live processing stats */}
        <div className="flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-md border border-custom">
          <Radio className="h-3.5 w-3.5 text-blue-400 animate-pulse" />
          <span className="text-gray-300">ACTIVE INFERENCE: {activeDetections} CHANNELS</span>
        </div>

        {/* Critical alert flag */}
        {criticalAlertCount > 0 && (
          <div className="flex items-center gap-2 bg-red-950/40 border border-red-500/30 px-3 py-1.5 rounded-md text-red-400 animate-alert-pulse">
            <AlertTriangle className="h-3.5 w-3.5" />
            <span>CRITICAL EVENTS: {criticalAlertCount}</span>
          </div>
        )}
      </div>
    </header>
  );
}
