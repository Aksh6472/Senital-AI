'use client';

import React from 'react';
import { mockAnalytics } from '../../lib/mockData';
import { BarChart3, AlertTriangle, ShieldCheck, Cpu } from 'lucide-react';

export function AnalyticsDashboard() {
  const { incidentCounts, hourlyTrends, accuracyByModule } = mockAnalytics;

  return (
    <div className="flex flex-col gap-6 w-full font-mono">
      
      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <div className="glass-panel p-5 rounded-xl border border-custom bg-red-950/10 flex justify-between items-center">
          <div>
            <span className="text-[10px] text-red-400 font-bold block mb-1">CRITICAL INCIDENTS</span>
            <span className="text-2xl font-bold text-white">{incidentCounts.critical}</span>
          </div>
          <AlertTriangle className="h-8 w-8 text-red-500/50" />
        </div>

        <div className="glass-panel p-5 rounded-xl border border-custom bg-orange-950/10 flex justify-between items-center">
          <div>
            <span className="text-[10px] text-orange-400 font-bold block mb-1">HIGH SEVERITY</span>
            <span className="text-2xl font-bold text-white">{incidentCounts.high}</span>
          </div>
          <AlertTriangle className="h-8 w-8 text-orange-500/50" />
        </div>

        <div className="glass-panel p-5 rounded-xl border border-custom bg-yellow-950/10 flex justify-between items-center">
          <div>
            <span className="text-[10px] text-yellow-400 font-bold block mb-1">MEDIUM SEVERITY</span>
            <span className="text-2xl font-bold text-white">{incidentCounts.medium}</span>
          </div>
          <AlertTriangle className="h-8 w-8 text-yellow-500/50" />
        </div>

        <div className="glass-panel p-5 rounded-xl border border-custom bg-blue-950/10 flex justify-between items-center">
          <div>
            <span className="text-[10px] text-blue-400 font-bold block mb-1">LOW SEVERITY</span>
            <span className="text-2xl font-bold text-white">{incidentCounts.low}</span>
          </div>
          <AlertTriangle className="h-8 w-8 text-blue-500/50" />
        </div>

      </div>

      {/* Grid of details */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        
        {/* Detection accuracy performance matrix */}
        <div className="glass-panel p-5 rounded-xl border border-custom bg-black/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4 border-b border-custom pb-3">
              <Cpu className="h-4.5 w-4.5 text-blue-400 animate-pulse" />
              <span className="text-xs font-bold text-white uppercase">AI MODULE INFERENCE ACCURACY MATRIX</span>
            </div>

            <div className="space-y-4">
              {accuracyByModule.map((item) => (
                <div key={item.module} className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-300">
                    <span>{item.module.toUpperCase()}</span>
                    <span>PRECISION: {item.precision}% | RECALL: {item.recall}%</span>
                  </div>

                  <div className="h-2 w-full bg-black/40 rounded overflow-hidden flex border border-custom">
                    {/* Precision bar */}
                    <div 
                      style={{ width: `${item.precision}%` }} 
                      className="bg-blue-600 h-full"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Hourly incident alert distributions */}
        <div className="glass-panel p-5 rounded-xl border border-custom bg-black/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4 border-b border-custom pb-3">
              <BarChart3 className="h-4.5 w-4.5 text-blue-400" />
              <span className="text-xs font-bold text-white uppercase">24-HOUR INCIDENTS DISTRIBUTION TREND</span>
            </div>

            <div className="flex items-end justify-between h-44 pt-6 gap-2">
              {hourlyTrends.map((trend) => {
                const maxCount = Math.max(...hourlyTrends.map(t => t.counts));
                const percentage = (trend.counts / maxCount) * 100;
                return (
                  <div key={trend.hour} className="flex-1 flex flex-col items-center gap-2">
                    <div className="text-[10px] text-gray-500 font-bold">{trend.counts}</div>
                    
                    <div className="w-full bg-black/40 border border-custom rounded-t overflow-hidden h-24 flex items-end">
                      <div 
                        style={{ height: `${percentage}%` }} 
                        className="bg-blue-600/70 hover:bg-blue-500 transition-colors w-full"
                      />
                    </div>

                    <div className="text-[10px] text-gray-500 font-bold">{trend.hour}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
