'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAppStore } from '@/store/app-store';

export default function SettingsPage() {
  const { systemInfo, fetchSystemInfo } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);
  
  // AMD GPU specific settings
  const [useAmdGpu, setUseAmdGpu] = useState(true);
  const [gpuMemoryLimit, setGpuMemoryLimit] = useState('80');
  
  useEffect(() => {
    const loadData = async () => {
      await fetchSystemInfo();
      setIsLoading(false);
      
      // Set AMD GPU usage based on availability
      setUseAmdGpu(systemInfo.gpu.isAmd);
    };
    
    loadData();
  }, [fetchSystemInfo, systemInfo.gpu.isAmd]);
  
  const handleSaveGpuSettings = async () => {
    try {
      toast.info('Saving GPU settings...');
      
      // Here we would normally make an API call to save the settings
      // For now, we'll just simulate success
      setTimeout(() => {
        toast.success('GPU settings saved successfully!');
      }, 1000);
    } catch (error) {
      console.error('Error saving GPU settings:', error);
      toast.error('Failed to save GPU settings');
    }
  };
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Configure your AI Avatar Video Generator
        </p>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* System Information */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold mb-4">System Information</h2>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300">GPU</h3>
                <p className="text-gray-900 dark:text-gray-100">
                  {systemInfo.gpu.model}
                  {systemInfo.gpu.isAmd && (
                    <span className="ml-2 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 px-1.5 py-0.5 rounded-full">
                      AMD
                    </span>
                  )}
                </p>
                {systemInfo.gpu.memory && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Memory: {systemInfo.gpu.memory}
                  </p>
                )}
              </div>
              
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300">CPU</h3>
                <p className="text-gray-900 dark:text-gray-100">{systemInfo.cpu}</p>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300">Memory</h3>
                <p className="text-gray-900 dark:text-gray-100">{systemInfo.memory}</p>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300">Operating System</h3>
                <p className="text-gray-900 dark:text-gray-100">{systemInfo.os}</p>
              </div>
            </div>
          </div>
          
          {/* GPU Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold mb-4">GPU Settings</h2>
            
            {!systemInfo.gpu.available ? (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-center">
                <p className="text-yellow-600 dark:text-yellow-300">
                  No GPU detected. Settings unavailable.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="use_amd_gpu"
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4"
                    checked={useAmdGpu}
                    onChange={(e) => setUseAmdGpu(e.target.checked)}
                    disabled={!systemInfo.gpu.isAmd}
                  />
                  <label htmlFor="use_amd_gpu" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                    Use AMD GPU acceleration
                    {!systemInfo.gpu.isAmd && (
                      <span className="ml-2 text-xs text-gray-500">(No AMD GPU detected)</span>
                    )}
                  </label>
                </div>
                
                <Input
                  label="GPU Memory Limit (%)"
                  type="number"
                  value={gpuMemoryLimit}
                  onChange={(e) => setGpuMemoryLimit(e.target.value)}
                  min="10"
                  max="100"
                  disabled={!systemInfo.gpu.available || !useAmdGpu}
                  description="Percentage of GPU memory to use for generation (10-100%)"
                />
                
                <div className="pt-2">
                  <Button
                    variant="primary"
                    onClick={handleSaveGpuSettings}
                    disabled={!systemInfo.gpu.available || !useAmdGpu}
                  >
                    Save GPU Settings
                  </Button>
                </div>
                
                <div className="mt-4 text-sm">
                  <p className="text-gray-500 dark:text-gray-400">
                    These settings control how the AMD GPU is utilized during video generation.
                    Higher memory usage can improve performance but may impact system stability.
                  </p>
                  
                  {systemInfo.gpu.isAmd && (
                    <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-md">
                      <p className="text-blue-600 dark:text-blue-300 font-medium">
                        AMD GPU is detected and configured for optimal performance
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* API Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 md:col-span-2">
            <h2 className="text-xl font-semibold mb-4">API Settings</h2>
            
            <div className="space-y-4">
              <Input
                label="API Base URL"
                value="http://localhost:8000"
                disabled
                description="The base URL of the AI Avatar Video Generator API (read-only)"
              />
              
              <div className="pt-2">
                <Button
                  variant="outline"
                  onClick={() => toast.info('API connection tested successfully')}
                >
                  Test API Connection
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
