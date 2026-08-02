'use client';

import React, { useState, useEffect } from 'react';
import { Camera, Incident } from '../lib/mockData';
import { api } from '../lib/api';
import { useWebSocket } from '../lib/useWebSocket';

// Layout Components
import { Header } from '../components/layout/Header';
import { Sidebar } from '../components/layout/Sidebar';

// Module Components
import { SOCDashboard } from '../components/dashboard/SOCDashboard';
import { CameraGrid } from '../components/cameras/CameraGrid';
import { CameraDetailModal } from '../components/cameras/CameraDetailModal';
import { IncidentFeed } from '../components/incidents/IncidentFeed';
import { EvidenceViewer } from '../components/evidence/EvidenceViewer';
import { GISMapView } from '../components/map/GISMapView';
import { AnalyticsDashboard } from '../components/analytics/AnalyticsDashboard';

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  
  // Real-time State
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  // Load Initial Data
  useEffect(() => {
    async function loadData() {
      const initialCams = await api.getCameras();
      const initialIncs = await api.getIncidents();
      setCameras(initialCams);
      setIncidents(initialIncs);
    }
    loadData();
  }, []);

  // Set up WebSocket alert listener / Simulation updates
  const { isConnected, activeDetectionsCount } = useWebSocket((newInc) => {
    // Append to live incident queue
    setIncidents(prev => [newInc, ...prev]);
  });

  // Triage Action Handlers
  const handleConfirmIncident = async (id: string) => {
    const updated = await api.confirmIncident(id);
    setIncidents(prev => prev.map(inc => inc.id === id ? updated : inc));
    if (selectedIncident?.id === id) {
      setSelectedIncident(updated);
    }
  };

  const handleDismissIncident = async (id: string) => {
    const updated = await api.dismissIncident(id);
    setIncidents(prev => prev.map(inc => inc.id === id ? updated : inc));
    if (selectedIncident?.id === id) {
      setSelectedIncident(updated);
    }
  };

  const handleEscalateIncident = async (id: string) => {
    const updated = await api.escalateIncident(id);
    setIncidents(prev => prev.map(inc => inc.id === id ? updated : inc));
    if (selectedIncident?.id === id) {
      setSelectedIncident(updated);
    }
  };

  // Toggle Module Toggles
  const handleToggleModule = async (cameraId: string, moduleName: string) => {
    const updated = await api.toggleCameraModule(cameraId, moduleName);
    setCameras(prev => prev.map(cam => cam.id === cameraId ? updated : cam));
    if (selectedCamera?.id === cameraId) {
      setSelectedCamera(updated);
    }
  };

  const handleSelectCamera = (camera: Camera) => {
    setSelectedCamera(camera);
  };

  const handleSelectIncident = (incident: Incident) => {
    setSelectedIncident(incident);
    setActiveTab('evidence');
  };

  const handleDownloadReport = async (id: string) => {
    await api.downloadReport(id);
  };

  const pendingTriageCount = incidents.filter(i => i.status === 'pending').length;
  const criticalAlertCount = incidents.filter(i => i.status === 'pending' && i.severity === 'critical').length;

  return (
    <div className="min-h-screen bg-[#02040a] text-gray-100 flex flex-col selection:bg-blue-600/30">
      
      {/* Header bar */}
      <Header 
        isConnected={isConnected} 
        activeDetections={activeDetectionsCount} 
        criticalAlertCount={criticalAlertCount} 
      />

      <div className="flex flex-1 flex-row">
        {/* Navigation Sidebar */}
        <Sidebar 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          pendingCount={pendingTriageCount} 
        />

        {/* Dynamic Tab Pane Render */}
        <main className="flex-1 p-6 overflow-y-auto max-h-[calc(100vh-64px)] bg-[#02040a]/40">
          <div className="max-w-7xl mx-auto space-y-6">
            
            {activeTab === 'dashboard' && (
              <SOCDashboard 
                cameras={cameras} 
                incidents={incidents} 
                setActiveTab={setActiveTab} 
                onSelectIncident={handleSelectIncident} 
              />
            )}

            {activeTab === 'cameras' && (
              <CameraGrid 
                cameras={cameras} 
                onToggleModule={handleToggleModule} 
                onSelectCamera={handleSelectCamera} 
              />
            )}

            {activeTab === 'incidents' && (
              <IncidentFeed 
                incidents={incidents} 
                onConfirm={handleConfirmIncident} 
                onDismiss={handleDismissIncident} 
                onEscalate={handleEscalateIncident} 
                onSelectIncident={handleSelectIncident} 
              />
            )}

            {activeTab === 'evidence' && (
              <EvidenceViewer 
                selectedIncident={selectedIncident} 
                onDownloadReport={handleDownloadReport} 
              />
            )}

            {activeTab === 'map' && (
              <GISMapView 
                cameras={cameras} 
                incidents={incidents} 
                onSelectCamera={handleSelectCamera} 
                onSelectIncident={handleSelectIncident} 
              />
            )}

            {activeTab === 'analytics' && (
              <AnalyticsDashboard />
            )}

          </div>
        </main>
      </div>

      {/* Expanded Camera Live Feed Stream Modal */}
      {selectedCamera && (
        <CameraDetailModal 
          camera={selectedCamera} 
          onClose={() => setSelectedCamera(null)} 
        />
      )}

    </div>
  );
}
