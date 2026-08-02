'use client';

import React from 'react';

interface TimelineEvent {
  time: string;
  event: string;
  type: string; // 'system' | 'ai' | 'user' | 'dispatch'
}

interface TimelineViewProps {
  timeline: TimelineEvent[];
}

export function TimelineView({ timeline }: TimelineViewProps) {
  const getMarkerColor = (type: string) => {
    switch (type) {
      case 'system': return 'bg-gray-600 border-gray-400';
      case 'ai': return 'bg-blue-600 border-blue-400 animate-pulse';
      case 'user': return 'bg-green-600 border-green-400';
      case 'dispatch': return 'bg-red-600 border-red-400';
      default: return 'bg-gray-600 border-gray-400';
    }
  };

  return (
    <div className="relative pl-6 border-l border-custom space-y-6 ml-3 my-4">
      {timeline.map((item, index) => (
        <div key={index} className="relative">
          {/* Node marker dot */}
          <span className={`absolute -left-[31px] top-1 h-3.5 w-3.5 rounded-full border-2 ${getMarkerColor(item.type)}`} />
          
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] text-gray-500 font-bold">{item.time}</span>
            <span className="text-xs text-gray-300">{item.event}</span>
            <span className="text-[9px] font-semibold text-gray-600 uppercase tracking-widest mt-0.5">
              SOURCE: {item.type}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
