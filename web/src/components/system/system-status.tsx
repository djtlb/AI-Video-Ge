"use client";

import { useEffect, useState } from 'react';
import { useAppStore } from '@/store/app-store';

export function SystemStatus() {
  const { systemInfo, fetchSystemInfo } = useAppStore();
  const [statusExpanded, setStatusExpanded] = useState(false);

  useEffect(() => {
    fetchSystemInfo();
    // Refresh system info every 60 seconds
    const interval = setInterval(() => {
      fetchSystemInfo();
    }, 60000);
    
    return () => clearInterval(interval);
  }, [fetchSystemInfo]);

  // AMD GPU-specific status indicator
  const gpuStatus = systemInfo.gpu.available ? (
    <span className="flex items-center">
      <span className={`h-2 w-2 rounded-full mr-2 ${systemInfo.gpu.isAmd ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
      {systemInfo.gpu.isAmd ? 'AMD GPU Active' : 'GPU Active'}
    </span>
  ) : (
    <span className="flex items-center">
      <span className="h-2 w-2 rounded-full bg-red-500 mr-2"></span>
      No GPU
    </span>
  );

  return (
    <div className="relative">
      <button
        onClick={() => setStatusExpanded(!statusExpanded)}
        className="flex items-center px-3 py-1.5 text-sm border border-gray-200 rounded-md dark:border-gray-700"
      >
        {gpuStatus}
      </button>
      
      {statusExpanded && (
        <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-900 rounded-md shadow-lg p-4 text-sm border border-gray-200 dark:border-gray-700 z-50">
          <h3 className="font-medium mb-2">System Information</h3>
          <div className="space-y-2">
            <div>
              <span className="text-gray-500 dark:text-gray-400">GPU:</span>{' '}
              <span className="font-medium">{systemInfo.gpu.model}</span>
              {systemInfo.gpu.isAmd && (
                <span className="ml-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 px-1.5 py-0.5 rounded-full">
                  AMD
                </span>
              )}
            </div>
            {systemInfo.gpu.memory && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">GPU Memory:</span>{' '}
                <span className="font-medium">{systemInfo.gpu.memory}</span>
              </div>
            )}
            <div>
              <span className="text-gray-500 dark:text-gray-400">CPU:</span>{' '}
              <span className="font-medium">{systemInfo.cpu}</span>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Memory:</span>{' '}
              <span className="font-medium">{systemInfo.memory}</span>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">OS:</span>{' '}
              <span className="font-medium">{systemInfo.os}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
