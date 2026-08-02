'use client';

import React, { useState } from 'react';
import { Camera } from '../../lib/mockData';
import { CameraCard } from './CameraCard';

interface CameraGridProps {
  cameras: Camera[];
  onToggleModule: (id: string, moduleName: string) => void;
  onSelectCamera: (camera: Camera) => void;
}

export function CameraGrid({ cameras, onToggleModule, onSelectCamera }: CameraGridProps) {
  const [selectedSite, setSelectedSite] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  const sites = ['all', ...Array.from(new Set(cameras.map(c => c.site)))];

  const filteredCameras = cameras.filter(cam => {
    const siteMatch = selectedSite === 'all' || cam.site === selectedSite;
    const statusMatch = selectedStatus === 'all' || cam.status === selectedStatus;
    return siteMatch && statusMatch;
  });

  return (
    <div className="flex flex-col gap-6 w-full">
      <div className="flex flex-wrap items-center justify-between gap-4 bg-black/30 p-4 rounded-xl border border-custom glass-panel">
        <div className="flex items-center gap-4">
          <div>
            <label className="block text-[10px] font-mono text-gray-400 mb-1">SITE FILTER</label>
            <select
              value={selectedSite}
              onChange={(e) => setSelectedSite(e.target.value)}
              className="bg-black/50 border border-custom rounded px-3 py-1.5 text-xs text-gray-200 font-mono focus:outline-none focus:border-blue-500/50"
            >
              {sites.map(s => (
                <option key={s} value={s}>{s.toUpperCase()}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-mono text-gray-400 mb-1">STATUS FILTER</label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-black/50 border border-custom rounded px-3 py-1.5 text-xs text-gray-200 font-mono focus:outline-none focus:border-blue-500/50"
            >
              <option value="all">ALL STATUSES</option>
              <option value="online">ONLINE</option>
              <option value="degraded">DEGRADED</option>
              <option value="offline">OFFLINE</option>
            </select>
          </div>
        </div>

        <div className="text-[10px] font-mono text-gray-400">
          SHOWING {filteredCameras.length} OF {cameras.length} CHANNELS
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCameras.map((camera) => (
          <CameraCard
            key={camera.id}
            camera={camera}
            onToggleModule={onToggleModule}
            onSelectCamera={onSelectCamera}
          />
        ))}
      </div>
    </div>
  );
}
