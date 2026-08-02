export interface Camera {
  id: string;
  name: string;
  site: string;
  zone: string;
  status: 'online' | 'offline' | 'degraded';
  streamUrl: string;
  activeModules: string[];
  fps: number;
  resolution: string;
  location: { lat: number; lng: number };
}

export interface Incident {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'pending' | 'confirmed' | 'dismissed' | 'escalated';
  message: string;
  cameraName: string;
  cameraId: string;
  timestamp: string;
  thumbnail: string;
  explanation: string;
  location: { lat: number; lng: number };
  evidence: EvidenceItem[];
  timeline: { time: string; event: string; type: string }[];
}

export interface EvidenceItem {
  id: string;
  type: 'video_clip' | 'frame_snapshot';
  mediaUrl: string;
  timestamp: string;
  metadata: {
    objectType?: string;
    confidence?: number;
    boundingBox?: [number, number, number, number]; // [x, y, w, h] normalized
  };
}

export const initialCameras: Camera[] = [
  {
    id: 'CAM-01',
    name: 'Main Entrance Gate',
    site: 'HQ Campus',
    zone: 'Perimeter West',
    status: 'online',
    streamUrl: '/placeholder-video-1.mp4',
    activeModules: ['Weapon Detection', 'Intrusion Detection'],
    fps: 30,
    resolution: '1080p',
    location: { lat: 37.7749, lng: -122.4194 }
  },
  {
    id: 'CAM-02',
    name: 'Server Room Alpha',
    site: 'HQ Campus',
    zone: 'Secure Area Room 1',
    status: 'online',
    streamUrl: '/placeholder-video-2.mp4',
    activeModules: ['Intrusion Detection', 'Tailgating Detection'],
    fps: 24,
    resolution: '1080p',
    location: { lat: 37.7752, lng: -122.4188 }
  },
  {
    id: 'CAM-03',
    name: 'Loading Dock B',
    site: 'Warehouse Site 2',
    zone: 'Perimeter East',
    status: 'degraded',
    activeModules: ['Object Detection', 'Loitering Detection'],
    streamUrl: '/placeholder-video-3.mp4',
    fps: 15,
    resolution: '720p',
    location: { lat: 37.7745, lng: -122.4210 }
  },
  {
    id: 'CAM-04',
    name: 'South Parking Structure Floor 2',
    site: 'HQ Campus',
    zone: 'Parking Zone D',
    status: 'online',
    streamUrl: '/placeholder-video-4.mp4',
    activeModules: ['Intrusion Detection', 'License Plate Reader'],
    fps: 30,
    resolution: '1080p',
    location: { lat: 37.7738, lng: -122.4199 }
  },
  {
    id: 'CAM-05',
    name: 'Executive Boardroom',
    site: 'HQ Campus',
    zone: 'Executive Wing',
    status: 'offline',
    streamUrl: '',
    activeModules: ['Intrusion Detection'],
    fps: 0,
    resolution: 'N/A',
    location: { lat: 37.7758, lng: -122.4175 }
  }
];

export const initialIncidents: Incident[] = [
  {
    id: 'INC-2026-9812',
    type: 'Weapon Detection',
    severity: 'critical',
    status: 'pending',
    message: 'Potential handgun detected in Perimeter West area.',
    cameraName: 'Main Entrance Gate',
    cameraId: 'CAM-01',
    timestamp: new Date(Date.now() - 3 * 60000).toISOString(), // 3 mins ago
    thumbnail: 'weapon_frame_1.jpg',
    explanation: 'Object detection model YOLOv8 identified a metallic hand-held object with 89.4% confidence matching handgun signature profiles. Subject is wearing dark coat.',
    location: { lat: 37.7749, lng: -122.4194 },
    timeline: [
      { time: '19:48:12', event: 'Frame captured by CAM-01', type: 'system' },
      { time: '19:48:13', event: 'Object detection flagged firearm (89.4% confidence)', type: 'ai' },
      { time: '19:48:15', event: 'Confidence Aggregator triggered severity elevation to CRITICAL', type: 'ai' },
      { time: '19:48:16', event: 'Notification policy dispatched SMS alerts to Security Team 1', type: 'dispatch' }
    ],
    evidence: [
      {
        id: 'EVI-001',
        type: 'frame_snapshot',
        mediaUrl: '/mock-frames/weapon_frame_1.jpg',
        timestamp: new Date(Date.now() - 3 * 60000).toISOString(),
        metadata: {
          objectType: 'Handgun',
          confidence: 0.89,
          boundingBox: [0.35, 0.48, 0.12, 0.08]
        }
      }
    ]
  },
  {
    id: 'INC-2026-9811',
    type: 'Intrusion Detection',
    severity: 'high',
    status: 'confirmed',
    message: 'Person detected crossing boundary fence during lockup hour.',
    cameraName: 'Loading Dock B',
    cameraId: 'CAM-03',
    timestamp: new Date(Date.now() - 25 * 60000).toISOString(), // 25 mins ago
    thumbnail: 'intruder_dock.jpg',
    explanation: 'Bounding box crossed tripwire line L-4 in restricted Zone Perimeter East. Duration of presence: 42 seconds.',
    location: { lat: 37.7745, lng: -122.4210 },
    timeline: [
      { time: '19:26:01', event: 'Subject detected at boundary perimeter', type: 'ai' },
      { time: '19:26:10', event: 'Aggregator validated loitering duration threshold', type: 'ai' },
      { time: '19:26:15', event: 'Incident registered and flagged as HIGH severity', type: 'system' },
      { time: '19:28:40', event: 'Officer Martinez confirmed presence and dispatched guard patrol', type: 'user' }
    ],
    evidence: [
      {
        id: 'EVI-002',
        type: 'frame_snapshot',
        mediaUrl: '/mock-frames/intruder_dock.jpg',
        timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
        metadata: {
          objectType: 'Person',
          confidence: 0.94,
          boundingBox: [0.65, 0.22, 0.20, 0.68]
        }
      }
    ]
  },
  {
    id: 'INC-2026-9810',
    type: 'Tailgating Detection',
    severity: 'medium',
    status: 'dismissed',
    message: 'Two subjects entered Secure Room 1 door on single badge event.',
    cameraName: 'Server Room Alpha',
    cameraId: 'CAM-02',
    timestamp: new Date(Date.now() - 60 * 60000).toISOString(), // 1 hour ago
    thumbnail: 'tailgate_1.jpg',
    explanation: 'Fast badge verification detected badge in event count of 1. Computer Vision tracker identified secondary person follow-through within 0.8 seconds.',
    location: { lat: 37.7752, lng: -122.4188 },
    timeline: [
      { time: '18:51:22', event: 'Card Reader badge event registered', type: 'system' },
      { time: '18:51:23', event: 'Tracking module identified dual-pass entry flow', type: 'ai' },
      { time: '18:51:30', event: 'Alert raised to operator', type: 'system' },
      { time: '18:54:10', event: 'Operator dismissed: Approved visitor guest escort', type: 'user' }
    ],
    evidence: [
      {
        id: 'EVI-003',
        type: 'frame_snapshot',
        mediaUrl: '/mock-frames/tailgate_1.jpg',
        timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
        metadata: {
          objectType: 'Tailgating Incident',
          confidence: 0.76,
          boundingBox: [0.42, 0.15, 0.35, 0.70]
        }
      }
    ]
  }
];

export const responderLocations = [
  { id: 'RESP-01', name: 'West Sector Patrol (Unit 4)', lat: 37.7742, lng: -122.4208, type: 'Patrol Car', status: 'available' },
  { id: 'RESP-02', name: 'Main Lobby Reception Desk', lat: 37.7754, lng: -122.4185, type: 'Security Officer', status: 'on-site' },
  { id: 'RESP-03', name: 'City Police Station (Sector 3)', lat: 37.7712, lng: -122.4230, type: 'Emergency Responder', status: 'dispatched' }
];

export const mockAnalytics = {
  incidentCounts: {
    critical: 4,
    high: 12,
    medium: 29,
    low: 54
  },
  hourlyTrends: [
    { hour: '00:00', counts: 5 },
    { hour: '04:00', counts: 2 },
    { hour: '08:00', counts: 14 },
    { hour: '12:00', counts: 22 },
    { hour: '16:00', counts: 18 },
    { hour: '20:00', counts: 25 }
  ],
  accuracyByModule: [
    { module: 'Weapon Detection', precision: 92.4, recall: 88.0 },
    { module: 'Intrusion Detection', precision: 98.1, recall: 97.5 },
    { module: 'Tailgating Detection', precision: 84.5, recall: 81.2 },
    { module: 'Loitering Detection', precision: 89.8, recall: 93.0 }
  ]
};
