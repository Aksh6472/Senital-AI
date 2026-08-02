'use client';

import React from 'react';
import { Camera } from '../../lib/mockData';
import { X, ShieldAlert, Cpu, Eye, Info } from 'lucide-react';

interface CameraDetailModalProps {
  camera: Camera;
  onClose: () => void;
}

export function CameraDetailModal({ camera, onClose }: CameraDetailModalProps) {
  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[#0b0f19] border border-custom w-full max-w-4xl rounded-2xl overflow-hidden shadow-2xl flex flex-col md:flex-row h-[550px]">
        
        {/* Large Stream Viewer with Overlay Target Bounding Boxes */}
        <div className="flex-1 bg-black relative flex items-center justify-center overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(#388bfd_1px,transparent_1px)] opacity-[0.03] [background-size:16px_16px] z-10" />
          <div className="scanner-overlay absolute inset-0 opacity-20 pointer-events-none" />

          {/* Simulated Bounding Box Overlay */}
          {camera.activeModules.includes('Weapon Detection') && camera.id === 'CAM-01' && (
            <div className="absolute border-2 border-red-500 bg-red-500/10 rounded px-2 py-1 font-mono text-[9px] text-white flex flex-col" style={{ top: '35%', left: '30%', width: '120px', height: '90px' }}>
              <span className="bg-red-600 px-1 rounded self-start font-bold">WEAPON (89%)</span>
              <span className="text-red-300 mt-1">HANDGUN</span>
            </div>
          )}

          {camera.activeModules.includes('Intrusion Detection') && camera.id === 'CAM-03' && (
            <div className="absolute border-2 border-yellow-500 bg-yellow-500/10 rounded px-2 py-1 font-mono text-[9px] text-white flex flex-col" style={{ top: '25%', left: '50%', width: '100px', height: '180px' }}>
              <span className="bg-yellow-600 px-1 rounded self-start font-bold">INTRUDER (94%)</span>
              <span className="text-yellow-300 mt-1">CROSS PERIMETER</span>
            </div>
          )}

          <div className="absolute top-4 left-4 z-20 flex items-center gap-2 bg-black/75 px-3 py-1 rounded-md text-xs font-mono border border-custom">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-white">{camera.name.toUpperCase()}</span>
            <span className="text-gray-500">|</span>
            <span className="text-gray-400">ZONE: {camera.zone}</span>
          </div>

          <div className="absolute bottom-4 right-4 z-20 bg-black/75 px-3 py-1 rounded-md text-[10px] font-mono border border-custom text-gray-400 flex items-center gap-2">
            <span>RES: {camera.resolution}</span>
            <span>FPS: {camera.fps}</span>
            <span>BITRATE: 4.2 Mbps</span>
          </div>

          {/* Tactical Crosshair design */}
          <div className="absolute inset-x-0 top-1/2 border-t border-white/5 pointer-events-none" />
          <div className="absolute inset-y-0 left-1/2 border-l border-white/5 pointer-events-none" />

          <div className="flex flex-col items-center gap-2 text-blue-500/40 font-mono text-sm z-15">
            <Eye className="h-16 w-16 animate-pulse" />
            <span className="tracking-widest text-[10px] text-gray-500 font-bold uppercase">FEED INGESTION ACTIVE</span>
          </div>
        </div>

        {/* Channel Details Sidebar Panel */}
        <div className="w-full md:w-80 border-t md:border-t-0 md:border-l border-custom p-6 flex flex-col justify-between h-full bg-[#0d111d]/90 font-mono">
          <div>
            <div className="flex justify-between items-start gap-4 mb-4">
              <div>
                <h2 className="text-base font-bold text-white leading-tight">{camera.name}</h2>
                <span className="text-[10px] text-gray-400 mt-1 block">{camera.site} • {camera.id}</span>
              </div>
              <button 
                onClick={onClose}
                className="text-gray-500 hover:text-gray-200 border border-transparent hover:border-custom p-1 rounded-lg transition-colors cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs mt-6">
              <div className="bg-black/40 p-3 rounded-lg border border-custom">
                <span className="text-[9px] text-gray-500 block font-bold mb-1">INFERENCE HARDWARE ASSIGNMENT</span>
                <div className="flex items-center gap-2 text-gray-300">
                  <Cpu className="h-4 w-4 text-blue-400" />
                  <span>NVIDIA TensorRT GPU 0 (CUDA)</span>
                </div>
              </div>

              <div>
                <span className="text-[9px] text-gray-500 block font-bold mb-1.5">ACTIVE MODULE ANALYSIS</span>
                <div className="space-y-1.5">
                  {camera.activeModules.length === 0 ? (
                    <span className="text-gray-500 text-[11px] italic">No active modules configured</span>
                  ) : (
                    camera.activeModules.map(mod => (
                      <div key={mod} className="flex items-center gap-2 text-gray-300 bg-blue-950/20 border border-blue-500/20 px-2 py-1 rounded">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
                        <span>{mod}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div>
                <span className="text-[9px] text-gray-500 block font-bold mb-1">GEOGRAPHICAL COORDINATES</span>
                <div className="text-gray-400 flex items-center gap-1">
                  <span className="text-gray-300">LAT:</span> {camera.location.lat.toFixed(4)}
                  <span className="text-gray-300 ml-2">LNG:</span> {camera.location.lng.toFixed(4)}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-950/20 border border-blue-500/20 p-3 rounded-lg flex gap-2 text-[10px] text-blue-400 leading-normal">
            <Info className="h-4.5 w-4.5 flex-shrink-0" />
            <span>AI frames are being processed with 4.5ms latency. Output signals sync live into Redis alerting pipelines.</span>
          </div>
        </div>

      </div>
    </div>
  );
}
