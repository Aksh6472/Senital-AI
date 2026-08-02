'use client';

import React, { useState } from 'react';
import { Camera, Incident, responderLocations } from '../../lib/mockData';
import { Video, ShieldAlert, Navigation, Layers, Shield } from 'lucide-react';

interface GISMapViewProps {
  cameras: Camera[];
  incidents: Incident[];
  onSelectCamera: (cam: Camera) => void;
  onSelectIncident: (inc: Incident) => void;
}

export function GISMapView({ cameras, incidents, onSelectCamera, onSelectIncident }: GISMapViewProps) {
  const [showResponders, setShowResponders] = useState(true);
  const [showCameras, setShowCameras] = useState(true);
  const [showIncidents, setShowIncidents] = useState(true);

  // Map bounding coordinates (centered roughly around mock lat/lng coordinates)
  // Lat: 37.7712 to 37.7762
  // Lng: -122.4235 to -122.4170
  const latMin = 37.7710;
  const latMax = 37.7765;
  const lngMin = -122.4235;
  const lngMax = -122.4168;

  // Convert GPS to SVG Coordinates percentage
  const getCoords = (lat: number, lng: number) => {
    const x = ((lng - lngMin) / (lngMax - lngMin)) * 100;
    const y = (1 - (lat - latMin) / (latMax - latMin)) * 100; // Invert y because SVG y goes down
    return { x: `${x}%`, y: `${y}%` };
  };

  const activeIncidents = incidents.filter(i => i.status === 'pending' || i.status === 'confirmed' || i.status === 'escalated');

  return (
    <div className="flex flex-col gap-6 w-full font-mono">
      
      {/* Map Control Board */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-black/30 p-4 rounded-xl border border-custom glass-panel">
        <div className="flex items-center gap-6">
          <span className="text-[10px] text-gray-500 font-bold tracking-widest">MAP LAYERS</span>
          
          <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
            <input 
              type="checkbox" 
              checked={showCameras} 
              onChange={() => setShowCameras(!showCameras)}
              className="rounded bg-black/40 border-custom text-blue-500 focus:ring-0 cursor-pointer"
            />
            <span className="flex items-center gap-1"><Video className="h-3.5 w-3.5 text-blue-400" /> CAMERAS</span>
          </label>

          <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
            <input 
              type="checkbox" 
              checked={showIncidents} 
              onChange={() => setShowIncidents(!showIncidents)}
              className="rounded bg-black/40 border-custom text-red-500 focus:ring-0 cursor-pointer"
            />
            <span className="flex items-center gap-1"><ShieldAlert className="h-3.5 w-3.5 text-red-400" /> INCIDENTS</span>
          </label>

          <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
            <input 
              type="checkbox" 
              checked={showResponders} 
              onChange={() => setShowResponders(!showResponders)}
              className="rounded bg-black/40 border-custom text-green-500 focus:ring-0 cursor-pointer"
            />
            <span className="flex items-center gap-1"><Navigation className="h-3.5 w-3.5 text-green-400" /> RESPONDERS</span>
          </label>
        </div>

        <div className="text-[10px] text-gray-400 flex items-center gap-2">
          <Layers className="h-3.5 w-3.5 text-blue-400" />
          <span>GIS COORDINATION HUB</span>
        </div>
      </div>

      {/* SVG Interactive Command Map */}
      <div className="relative h-[550px] bg-slate-950 border border-custom rounded-2xl overflow-hidden glass-panel">
        
        {/* Map Grid Pattern Background */}
        <div className="absolute inset-0 bg-[radial-gradient(#30363d_1px,transparent_1px)] opacity-[0.2] [background-size:24px_24px]" />
        
        {/* Abstract Architectural Site Blueprint Drawings */}
        <svg className="absolute inset-0 w-full h-full text-blue-500/10 pointer-events-none" xmlns="http://www.w3.org/2000/svg">
          {/* Main Ring perimeter road */}
          <path d="M 100 200 Q 300 100 700 150 T 900 450" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="5,5" />
          <path d="M 50 400 L 950 400" fill="none" stroke="currentColor" strokeWidth="1" />
          
          {/* Main Headquarters Building polygon */}
          <rect x="35%" y="25%" width="25%" height="30%" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <text x="36%" y="29%" className="fill-blue-500/30 text-[9px] font-bold font-mono">HQ COMPLEX - ALPHA WING</text>
          
          {/* Warehouse Site polygon */}
          <polygon points="150,120 280,100 250,220 120,240" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <text x="135" y="145" className="fill-blue-500/30 text-[9px] font-bold font-mono">WAREHOUSE SITE 2</text>
        </svg>

        {/* Pulsing Alert / Incident hot spots on Map */}
        {showIncidents && activeIncidents.map((inc) => {
          const coords = getCoords(inc.location.lat, inc.location.lng);
          return (
            <div
              key={inc.id}
              style={{ top: coords.y, left: coords.x }}
              className="absolute -translate-x-1/2 -translate-y-1/2 z-30 group cursor-pointer"
              onClick={() => onSelectIncident(inc)}
            >
              {/* Pulse rings */}
              <span className="absolute h-10 w-10 bg-red-500/20 rounded-full animate-ping -left-3 -top-3" />
              
              <div className="bg-red-600 border border-red-400 p-2 rounded-lg text-white shadow-xl flex items-center gap-1.5 transition-transform hover:scale-110">
                <ShieldAlert className="h-4 w-4" />
                <span className="text-[9px] font-bold">{inc.id.split('-')[2]}</span>
              </div>

              {/* Tooltip detail */}
              <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 w-48 bg-slate-900/95 border border-red-500/40 p-2.5 rounded shadow-2xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-40 text-[10px] space-y-1">
                <div className="text-red-400 font-bold uppercase">{inc.type}</div>
                <div className="text-gray-300">{inc.message}</div>
                <div className="text-gray-500">SEVERITY: {inc.severity.toUpperCase()}</div>
              </div>
            </div>
          );
        })}

        {/* Camera Nodes */}
        {showCameras && cameras.map((cam) => {
          const coords = getCoords(cam.location.lat, cam.location.lng);
          const isOffline = cam.status === 'offline';
          return (
            <div
              key={cam.id}
              style={{ top: coords.y, left: coords.x }}
              className="absolute -translate-x-1/2 -translate-y-1/2 z-20 group cursor-pointer"
              onClick={() => onSelectCamera(cam)}
            >
              <div className={`p-1.5 rounded-full border shadow-lg transition-transform hover:scale-110 ${
                isOffline
                  ? 'bg-red-950/80 border-red-500/30 text-red-400'
                  : 'bg-slate-900/90 border-blue-500/40 text-blue-400'
              }`}>
                <Video className="h-3.5 w-3.5" />
              </div>

              {/* Tooltip detail */}
              <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-44 bg-slate-900/95 border border-blue-500/40 p-2 rounded shadow-2xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-40 text-[10px] space-y-1">
                <div className="text-blue-400 font-bold">{cam.name}</div>
                <div className="text-gray-300">STATUS: {cam.status.toUpperCase()}</div>
                <div className="text-gray-500">ACTIVE CONTROLS: {cam.activeModules.length}</div>
              </div>
            </div>
          );
        })}

        {/* Responders */}
        {showResponders && responderLocations.map((resp) => {
          const coords = getCoords(resp.lat, resp.lng);
          return (
            <div
              key={resp.id}
              style={{ top: coords.y, left: coords.x }}
              className="absolute -translate-x-1/2 -translate-y-1/2 z-25 group"
            >
              <div className="bg-green-700/80 border border-green-400 p-1.5 rounded-md text-green-300 shadow-lg flex items-center justify-center">
                <Navigation className="h-3.5 w-3.5 transform rotate-45" />
              </div>

              {/* Tooltip detail */}
              <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 w-48 bg-slate-900/95 border border-green-500/40 p-2 rounded shadow-2xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-40 text-[10px] space-y-1">
                <div className="text-green-400 font-bold">{resp.name}</div>
                <div className="text-gray-300">TYPE: {resp.type}</div>
                <div className="text-gray-500">STATUS: {resp.status.toUpperCase()}</div>
              </div>
            </div>
          );
        })}

      </div>
    </div>
  );
}
