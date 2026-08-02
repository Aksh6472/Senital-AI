import { useEffect, useState } from 'react';
import { Incident, initialCameras } from './mockData';
import { api } from './api';

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_BASE_URL || '';

export function useWebSocket(onNewIncident?: (incident: Incident) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const [activeDetectionsCount, setActiveDetectionsCount] = useState(0);

  useEffect(() => {
    // If we have a backend WebSocket configured, use it
    if (WS_BASE_URL) {
      const ws = new WebSocket(`${WS_BASE_URL}/live/incidents`);
      
      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'incident' && onNewIncident) {
            onNewIncident(data.payload);
          }
        } catch (e) {
          console.error('Failed to parse websocket message', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
      };

      return () => {
        ws.close();
      };
    }

    // Otherwise, simulate a 24/7 active control room dashboard
    setIsConnected(true);

    const simulationIntervals: NodeJS.Timeout[] = [];

    // Simulate occasional incoming incidents (every 45-60 seconds)
    const incidentSim = setInterval(() => {
      const randomCam = initialCameras[Math.floor(Math.random() * initialCameras.length)];
      if (randomCam.status === 'offline') return;

      const incidentTypes = [
        { type: 'Intrusion Detection', severity: 'high', msg: 'Unauthorized person detected in perimeter zone.' },
        { type: 'Loitering Detection', severity: 'medium', msg: 'Subject observed loitering near back entrance for over 5 minutes.' },
        { type: 'Weapon Detection', severity: 'critical', msg: 'Potential rifle/firearm signature identified.' }
      ];

      const chosen = incidentTypes[Math.floor(Math.random() * incidentTypes.length)];
      const idNum = Math.floor(1000 + Math.random() * 9000);
      
      const newInc: Incident = {
        id: `INC-2026-${idNum}`,
        type: chosen.type,
        severity: chosen.severity as 'critical' | 'high' | 'medium' | 'low',
        status: 'pending',
        message: `${chosen.msg} (Simulated Live Event)`,
        cameraName: randomCam.name,
        cameraId: randomCam.id,
        timestamp: new Date().toISOString(),
        thumbnail: 'live_frame.jpg',
        explanation: `Automated AI detection alert generated for ${randomCam.name}. Model threshold exceeded standard boundary logic.`,
        location: randomCam.location,
        timeline: [
          { time: new Date().toLocaleTimeString(), event: `Frame captured by ${randomCam.name}`, type: 'system' },
          { time: new Date().toLocaleTimeString(), event: `AI flagged ${chosen.type}`, type: 'ai' }
        ],
        evidence: [
          {
            id: `EVI-${idNum}`,
            type: 'frame_snapshot',
            mediaUrl: '/mock-frames/live_frame.jpg',
            timestamp: new Date().toISOString(),
            metadata: {
              objectType: chosen.type.split(' ')[0],
              confidence: 0.85 + Math.random() * 0.12,
              boundingBox: [0.3, 0.3, 0.4, 0.4]
            }
          }
        ]
      };

      api.insertMockIncident(newInc);
      if (onNewIncident) {
        onNewIncident(newInc);
      }
    }, 45000);

    simulationIntervals.push(incidentSim);

    // Simulate active camera frame processing changes
    const activeDetSim = setInterval(() => {
      setActiveDetectionsCount(Math.floor(Math.random() * 5));
    }, 4000);

    simulationIntervals.push(activeDetSim);

    return () => {
      simulationIntervals.forEach(clearInterval);
    };
  }, [onNewIncident]);

  return { isConnected, activeDetectionsCount };
}
