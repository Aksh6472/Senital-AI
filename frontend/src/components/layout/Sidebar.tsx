'use client';

import React from 'react';
import { 
  LayoutDashboard, 
  Video, 
  AlertOctagon, 
  Search, 
  Map, 
  BarChart3 
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  pendingCount: number;
}

export function Sidebar({ activeTab, setActiveTab, pendingCount }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Command Center', icon: LayoutDashboard },
    { id: 'cameras', label: 'Camera Grid', icon: Video },
    { id: 'incidents', label: 'Incident Feed', icon: AlertOctagon, badge: pendingCount > 0 ? pendingCount : undefined },
    { id: 'evidence', label: 'Evidence Viewer', icon: Search },
    { id: 'map', label: 'GIS Command Map', icon: Map },
    { id: 'analytics', label: 'System Analytics', icon: BarChart3 }
  ];

  return (
    <aside className="w-64 border-r border-custom glass-panel flex flex-col justify-between py-6">
      <div className="flex flex-col gap-2 px-3">
        <p className="px-3 text-[10px] font-mono tracking-wider text-gray-500 font-semibold mb-2">OPERATIONS MENU</p>
        
        <nav className="flex flex-col gap-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all duration-150 font-mono ${
                  isActive 
                    ? 'bg-blue-600/15 border border-blue-500/40 text-blue-400 font-medium' 
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`h-4.5 w-4.5 ${isActive ? 'text-blue-400' : 'text-gray-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && (
                  <span className="bg-red-500/20 border border-red-500/40 text-red-400 text-[10px] font-bold px-2 py-0.5 rounded-full animate-pulse">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="px-6 font-mono text-[10px] text-gray-500 border-t border-custom pt-6">
        <div>DEPLOYMENT ID: SOC-HQ-01</div>
        <div>REGION: US-WEST-2</div>
        <div className="mt-1 flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 bg-green-500 rounded-full animate-pulse" />
          <span>INFERENCE RUNTIME ACTIVE</span>
        </div>
      </div>
    </aside>
  );
}
