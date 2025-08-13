'use client';

import { useState, useEffect } from 'react';
import { VideoPlayer } from '@/components/generation/video-player';
import { useAppStore } from '@/store/app-store';
import { formatDate } from '@/lib/utils';

export default function GalleryPage() {
  const { videos, fetchVideos } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  
  useEffect(() => {
    const loadData = async () => {
      await fetchVideos();
      setIsLoading(false);
    };
    
    loadData();
  }, [fetchVideos]);
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Video Gallery</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Browse and manage your generated videos
        </p>
      </div>
      
      {selectedVideo && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Selected Video</h2>
            <button 
              type="button"
              onClick={() => setSelectedVideo(null)}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              aria-label="Close video player"
              title="Close video player"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
              </svg>
            </button>
          </div>
          <VideoPlayer videoPath={selectedVideo} />
        </div>
      )}
      
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : videos.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No videos yet</h3>
          <p className="mt-1 text-gray-500 dark:text-gray-400">
            Generate some videos to see them here
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {videos.map((video) => (
            <div 
              key={video.video_path}
              className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-gray-200 dark:border-gray-700"
              onClick={() => setSelectedVideo(video.video_path)}
            >
              <div className="aspect-video bg-black relative">
                {/* Video thumbnail */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-12 h-12 text-white opacity-80">
                    <path fillRule="evenodd" d="M4.5 5.653c0-1.426 1.529-2.33 2.779-1.643l11.54 6.348c1.295.712 1.295 2.573 0 3.285L7.28 19.991c-1.25.687-2.779-.217-2.779-1.643V5.653z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 truncate">{video.name}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {formatDate(video.created_at)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
