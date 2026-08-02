'use client';

import React from 'react';
import { Camera } from '../../lib/mockData';
import { ShieldCheck, Video, HelpCircle, Eye, EyeOff } from 'lucide-react';

interface CameraCardProps {
  camera: Camera;
  onToggleModule: (id: string, moduleName: string) => void;
  onSelectCamera: (camera: Camera) => void;
}

export function CameraCard({ camera, onToggleModule, onSelectCamera }: CameraCardProps) {
  const statusColors = {
    online: 'bg-green-500',
    degraded: 'bg-yellow-500',
    offline: 'bg-red-500'
  };

  const allModules = ['Weapon Detection', 'Intrusion Detection', 'Tailgating Detection', 'Loitering Detection'];

  return (
    <div className="glass-panel rounded-xl overflow-hidden flex flex-col justify-between h-[360px] border border-custom">
      
      {/* Visual Live Stream Placeholder with Grid Scanner */}
      <div className="relative h-44 bg-slate-950 flex items-center justify-center overflow-hidden group">
        {camera.status === 'offline' ? (
          <div className="flex flex-col items-center gap-2 text-gray-500 font-mono text-xs">
            <EyeOff className="h-8 w-8 text-red-500/50" />
            <span>STREAM OFFLINE</span>
          </div>
        ) : (
          <>
            <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(0,0,0,0.4),rgba(0,0,0,0.8))] z-10" />
            {/* Grid Pattern */}
            <div className="absolute inset-0 opacity-[0.05] bg-[radial-gradient(#388bfd_1px,transparent_1px)] [background-size:16px_16px]" />
            <div className="absolute top-3 left-3 z-20 flex items-center gap-2 bg-black/60 px-2 py-0.5 rounded text-[10px] font-mono text-gray-300">
              <span className={`h-1.5 w-1.5 rounded-full ${statusColors[camera.status]} animate-pulse`} />
              <span>{camera.name.toUpperCase()}</span>
            </div>
            
            <div className="absolute top-3 right-3 z-20 bg-black/60 px-2 py-0.5 rounded text-[10px] font-mono text-gray-400">
              {camera.resolution} @ {camera.fps}fps
            </div>

            <div className="scanner-overlay absolute inset-0 opacity-40" />

            <div className="flex flex-col items-center gap-2 text-blue-400/60 font-mono text-xs z-15 group-hover:scale-105 transition-transform duration-300">
              <Video className="h-10 w-10 animate-pulse" />
              <span className="text-[10px] tracking-widest text-gray-400">LIVE FEED CHANNEL</span>
            </div>

            <button 
              onClick={() => onSelectCamera(camera)}
              className="absolute bottom-3 right-3 z-20 flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white font-mono text-[10px] px-2.5 py-1 rounded shadow-lg transition-colors cursor-pointer"
            >
              <Eye className="h-3 w-3" />
              <span>EXPAND</span>
            </button>
          </>
        )}
      </div>

      {/* Camera Specifications */}
      <div className="p-4 flex-1 flex flex-col justify-between bg-black/10">
        <div className="flex justify-between items-start gap-2">
          <div>
            <h3 className="font-bold text-sm text-gray-100">{camera.name}</h3>
            <p className="text-[10px] font-mono text-gray-400 mt-0.5">{camera.site} • {camera.zone}</p>
          </div>
          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
            camera.status === 'online' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
            camera.status === 'degraded' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
            'bg-red-500/10 text-red-400 border border-red-500/20'
          }`}>
            {camera.status.toUpperCase()}
          </span>
        </div>

        {/* AI Analytics Modules Settings */}
        <div className="mt-3">
          <p className="text-[9px] font-mono text-gray-500 font-bold mb-1.5 tracking-wider">AI MODULE DETECTION CONTROLS</p>
          <div className="flex flex-wrap gap-1.5">
            {allModules.map((mod) => {
              const isActive = camera.activeModules.includes(mod);
              return (
                <button
                  key={mod}
                  disabled={camera.status === 'offline'}
                  onClick={() => onToggleModule(camera.id, mod)}
                  className={`text-[9px] font-mono px-2 py-1 rounded border transition-all duration-150 cursor-pointer ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border-blue-500/40'
                      : 'bg-black/40 text-gray-500 border-transparent hover:border-gray-700 hover:text-gray-400'
                  } disabled:opacity-40 disabled:cursor-not-allowed`}
                >
                  {mod.replace(' Detection', '').toUpperCase()}
                </button>
              );
            })}
          </div>
        </div>
      </div>

    </div>
  );
}
