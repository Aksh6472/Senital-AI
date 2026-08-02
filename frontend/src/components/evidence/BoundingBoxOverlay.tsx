'use client';

import React from 'react';
import { EvidenceItem } from '../../lib/mockData';

interface BoundingBoxOverlayProps {
  evidence: EvidenceItem;
}

export function BoundingBoxOverlay({ evidence }: BoundingBoxOverlayProps) {
  if (evidence.type !== 'frame_snapshot' || !evidence.metadata.boundingBox) {
    return null;
  }

  // Normalized bounding boxes: [x, y, w, h] from 0 to 1
  const [x, y, w, h] = evidence.metadata.boundingBox;

  const style: React.CSSProperties = {
    position: 'absolute',
    left: `${x * 100}%`,
    top: `${y * 100}%`,
    width: `${w * 100}%`,
    height: `${h * 100}%`,
  };

  const confidencePct = evidence.metadata.confidence 
    ? Math.round(evidence.metadata.confidence * 100) 
    : null;

  return (
    <div 
      style={style} 
      className="border-2 border-red-500 bg-red-500/10 rounded flex flex-col font-mono text-[9px] text-white z-20"
    >
      <span className="bg-red-600 px-1 rounded self-start font-bold">
        {evidence.metadata.objectType?.toUpperCase() || 'TARGET'} {confidencePct ? `(${confidencePct}%)` : ''}
      </span>
    </div>
  );
}
