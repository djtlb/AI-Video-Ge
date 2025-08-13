'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAppStore } from '@/store/app-store';
import { VideoGenerationForm } from '@/components/generation/video-generation-form';
import { VideoPlayer } from '@/components/generation/video-player';
import { Button } from '@/components/ui/button';

export default function GeneratePage() {
  const { selectedCharacters, characters } = useAppStore();
  const [generatedVideoPath, setGeneratedVideoPath] = useState<string | null>(null);
  
  // Check if we have characters selected
  const hasSelectedCharacters = selectedCharacters.length > 0;
  
  // Get the names of selected characters
  const selectedCharacterNames = characters
    .filter(char => selectedCharacters.includes(char.id))
    .map(char => char.name);
  
  const handleGenerationSuccess = (videoPath: string) => {
    setGeneratedVideoPath(videoPath);
  };
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Generate Video</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Create videos with your selected characters
        </p>
      </div>
      
      {!hasSelectedCharacters ? (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 text-center">
          <h3 className="text-lg font-medium text-yellow-800 dark:text-yellow-200">No characters selected</h3>
          <p className="mt-1 text-yellow-600 dark:text-yellow-300">
            Please select at least one character from the Characters page
          </p>
          <Link href="/characters">
            <Button variant="outline" className="mt-4">
              Go to Characters
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="lg:sticky lg:top-24 space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold mb-4">Generation Settings</h2>
              
              <div className="mb-6">
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Selected Characters:</h3>
                <ul className="list-disc list-inside text-gray-600 dark:text-gray-400">
                  {selectedCharacterNames.map(name => (
                    <li key={name}>{name}</li>
                  ))}
                </ul>
              </div>
              
              <VideoGenerationForm onSuccess={handleGenerationSuccess} />
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold mb-4">Preview</h2>
              
              {generatedVideoPath ? (
                <VideoPlayer videoPath={generatedVideoPath} />
              ) : (
                <div className="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500 dark:text-gray-400">
                    Video preview will appear here after generation
                  </p>
                </div>
              )}
            </div>
            
            {generatedVideoPath && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-xl font-semibold mb-4">Actions</h2>
                <div className="flex flex-wrap gap-3">
                  <Button variant="outline" onClick={() => setGeneratedVideoPath(null)}>
                    Clear Preview
                  </Button>
                  <Link href="/gallery">
                    <Button variant="outline">
                      View All Videos
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
