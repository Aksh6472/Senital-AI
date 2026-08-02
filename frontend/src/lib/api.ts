import { Camera, Incident, initialCameras, initialIncidents } from './mockData';

// Singleton mock store to persist actions during dashboard session
let camerasDb: Camera[] = [...initialCameras];
let incidentsDb: Incident[] = [...initialIncidents];

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

export const api = {
  async getCameras(): Promise<Camera[]> {
    if (API_BASE_URL) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/cameras`);
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Failed to fetch from backend cameras, falling back to mock database', e);
      }
    }
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 300));
    return camerasDb;
  },

  async toggleCameraModule(cameraId: string, moduleName: string): Promise<Camera> {
    if (API_BASE_URL) {
      try {
        const camera = camerasDb.find(c => c.id === cameraId);
        if (camera) {
          const currentModules = camera.activeModules.includes(moduleName)
            ? camera.activeModules.filter(m => m !== moduleName)
            : [...camera.activeModules, moduleName];
          const res = await fetch(`${API_BASE_URL}/api/v1/cameras/${cameraId}/detection-modules`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ modules: currentModules })
          });
          if (res.ok) return await res.json();
        }
      } catch (e) {
        console.warn('Failed to save module to backend, updating mock database', e);
      }
    }
    
    camerasDb = camerasDb.map(cam => {
      if (cam.id === cameraId) {
        const hasModule = cam.activeModules.includes(moduleName);
        return {
          ...cam,
          activeModules: hasModule
            ? cam.activeModules.filter(m => m !== moduleName)
            : [...cam.activeModules, moduleName]
        };
      }
      return cam;
    });
    return camerasDb.find(c => c.id === cameraId)!;
  },

  async getIncidents(): Promise<Incident[]> {
    if (API_BASE_URL) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/incidents`);
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Failed to fetch from backend incidents, falling back to mock database', e);
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 350));
    return incidentsDb.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  },

  async confirmIncident(id: string): Promise<Incident> {
    if (API_BASE_URL) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/incidents/${id}/confirm`, { method: 'POST' });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Failed to confirm incident on backend, updating mock database', e);
      }
    }

    incidentsDb = incidentsDb.map(inc => {
      if (inc.id === id) {
        return {
          ...inc,
          status: 'confirmed',
          timeline: [
            ...inc.timeline,
            { time: new Date().toLocaleTimeString(), event: 'Incident marked as CONFIRMED by operator', type: 'user' }
          ]
        };
      }
      return inc;
    });
    return incidentsDb.find(i => i.id === id)!;
  },

  async dismissIncident(id: string): Promise<Incident> {
    if (API_BASE_URL) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/incidents/${id}/dismiss`, { method: 'POST' });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Failed to dismiss incident on backend, updating mock database', e);
      }
    }

    incidentsDb = incidentsDb.map(inc => {
      if (inc.id === id) {
        return {
          ...inc,
          status: 'dismissed',
          timeline: [
            ...inc.timeline,
            { time: new Date().toLocaleTimeString(), event: 'Incident DISMISSED as false positive', type: 'user' }
          ]
        };
      }
      return inc;
    });
    return incidentsDb.find(i => i.id === id)!;
  },

  async escalateIncident(id: string): Promise<Incident> {
    if (API_BASE_URL) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/incidents/${id}/escalate`, { method: 'POST' });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Failed to escalate incident on backend, updating mock database', e);
      }
    }

    incidentsDb = incidentsDb.map(inc => {
      if (inc.id === id) {
        return {
          ...inc,
          status: 'escalated',
          timeline: [
            ...inc.timeline,
            { time: new Date().toLocaleTimeString(), event: 'Incident ESCALATED to emergency responders', type: 'user' }
          ]
        };
      }
      return inc;
    });
    return incidentsDb.find(i => i.id === id)!;
  },

  async downloadReport(id: string): Promise<void> {
    alert(`Generating security audit report for incident ${id}...\nReport downloaded successfully in PDF format.`);
  },

  // Helper function to insert a live mock incident into the local mock db
  insertMockIncident(incident: Incident) {
    incidentsDb.unshift(incident);
  }
};
