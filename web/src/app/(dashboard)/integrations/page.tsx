'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAppStore } from '@/store/app-store';
import { api } from '@/services/api';
import { absoluteUrl } from '@/lib/utils';

export default function IntegrationsPage() {
  const { integrations, fetchIntegrationsStatus, selectedCharacters, characters } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);
  const [imagePrompt, setImagePrompt] = useState('');
  const [imageSize, setImageSize] = useState('medium');
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null);
  
  // Get the first selected character for talking avatar
  const selectedCharacter = selectedCharacters.length > 0 
    ? characters.find(c => c.id === selectedCharacters[0]) 
    : null;
  
  const [talkingText, setTalkingText] = useState('');
  const [isTalkingGeneration, setIsTalkingGeneration] = useState(false);
  const [talkingVideoPath, setTalkingVideoPath] = useState<string | null>(null);
  
  useEffect(() => {
    const loadData = async () => {
      await fetchIntegrationsStatus();
      setIsLoading(false);
    };
    
    loadData();
  }, [fetchIntegrationsStatus]);
  
  const handleGenerateImage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!imagePrompt.trim()) {
      toast.error('Please enter an image prompt');
      return;
    }
    
    setIsGeneratingImage(true);
    setGeneratedImageUrl(null);
    
    try {
      toast.info('Generating image...');
      
      const result = await api.generateAiImage(imagePrompt, imageSize);
      setGeneratedImageUrl(result);
      
      toast.success('Image generated successfully!');
    } catch (error) {
      console.error('Error generating image:', error);
      toast.error('Failed to generate image');
    } finally {
      setIsGeneratingImage(false);
    }
  };
  
  const handleGenerateTalkingAvatar = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedCharacter) {
      toast.error('Please select a character first');
      return;
    }
    
    if (!talkingText.trim()) {
      toast.error('Please enter text for the talking avatar');
      return;
    }
    
    setIsTalkingGeneration(true);
    setTalkingVideoPath(null);
    
    try {
      toast.info('Generating talking avatar video...');
      
      const result = await api.generateTalkingAvatar(
        selectedCharacter.id,
        talkingText,
        15, // duration in seconds
        true // use advanced motion
      );
      
      setTalkingVideoPath(result.video_path);
      toast.success('Talking avatar video generated successfully!');
    } catch (error) {
      console.error('Error generating talking avatar:', error);
      toast.error('Failed to generate talking avatar');
    } finally {
      setIsTalkingGeneration(false);
    }
  };
  
  // Check which integrations are available
  const isImageGeneratorAvailable = integrations?.modules?.image_generator;
  const isTalkingAvatarAvailable = integrations?.modules?.talking_avatar;
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">AI Integrations</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Use advanced AI capabilities from integrated services
        </p>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : !integrations.available ? (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 text-center">
          <h3 className="text-lg font-medium text-yellow-800 dark:text-yellow-200">Integrations Not Available</h3>
          <p className="mt-1 text-yellow-600 dark:text-yellow-300">
            The integrations API is not available. Please check your configuration.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image Generation */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold mb-4">AI Image Generation</h2>
            
            {!isImageGeneratorAvailable ? (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-center">
                <p className="text-yellow-600 dark:text-yellow-300">
                  Image generator integration is not available
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <form onSubmit={handleGenerateImage} className="space-y-4">
                  <Input
                    label="Image Prompt"
                    value={imagePrompt}
                    onChange={(e) => setImagePrompt(e.target.value)}
                    placeholder="Describe the image you want to generate"
                    disabled={isGeneratingImage}
                  />
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Image Size
                    </label>
                    <select
                      value={imageSize}
                      onChange={(e) => setImageSize(e.target.value)}
                      className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-50"
                      disabled={isGeneratingImage}
                    >
                      <option value="small">Small (256x256)</option>
                      <option value="medium">Medium (512x512)</option>
                      <option value="large">Large (1024x1024)</option>
                    </select>
                  </div>
                  
                  <div className="pt-2">
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isGeneratingImage}
                      disabled={isGeneratingImage || !imagePrompt.trim()}
                      className="w-full"
                    >
                      Generate Image
                    </Button>
                  </div>
                </form>
                
                {generatedImageUrl && (
                  <div className="mt-6">
                    <h3 className="font-medium mb-2">Generated Image:</h3>
                    <div className="rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                      <img 
                        src={generatedImageUrl} 
                        alt="Generated AI image" 
                        className="w-full h-auto"
                      />
                    </div>
                    <div className="mt-2 flex justify-end">
                      <a 
                        href={generatedImageUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
                      >
                        Open in New Tab
                      </a>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Talking Avatar */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold mb-4">Talking Avatar</h2>
            
            {!isTalkingAvatarAvailable ? (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-center">
                <p className="text-yellow-600 dark:text-yellow-300">
                  Talking avatar integration is not available
                </p>
              </div>
            ) : !selectedCharacter ? (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-center">
                <p className="text-yellow-600 dark:text-yellow-300">
                  Please select a character from the Characters page
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                    {selectedCharacter.thumb_path && (
                      <img 
                        src={absoluteUrl(selectedCharacter.thumb_path.startsWith('/') ? selectedCharacter.thumb_path : `/${selectedCharacter.thumb_path}`)} 
                        alt={selectedCharacter.name} 
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                  <div>
                    <p className="font-medium">{selectedCharacter.name}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Selected Character</p>
                  </div>
                </div>
                
                <form onSubmit={handleGenerateTalkingAvatar} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Text to Speak
                    </label>
                    <textarea
                      value={talkingText}
                      onChange={(e) => setTalkingText(e.target.value)}
                      placeholder="Enter text for the character to speak"
                      className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-50"
                      rows={4}
                      disabled={isTalkingGeneration}
                    ></textarea>
                  </div>
                  
                  <div className="pt-2">
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isTalkingGeneration}
                      disabled={isTalkingGeneration || !talkingText.trim()}
                      className="w-full"
                    >
                      Generate Talking Avatar
                    </Button>
                  </div>
                </form>
                
                {talkingVideoPath && (
                  <div className="mt-6">
                    <h3 className="font-medium mb-2">Generated Video:</h3>
                    <div className="aspect-video bg-black rounded-lg overflow-hidden">
                      <video 
                        src={absoluteUrl(`/download?video_path=${encodeURIComponent(talkingVideoPath)}`)}
                        controls
                        className="w-full h-full"
                      ></video>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Integrations Status */}
      {!isLoading && integrations.available && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-semibold mb-4">Integrations Status</h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(integrations.modules).map(([name, available]) => (
              <div key={name} className="flex items-center space-x-2">
                <span className={`h-2 w-2 rounded-full ${available ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="capitalize">{name.replace(/_/g, ' ')}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${available ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'}`}>
                  {available ? 'Available' : 'Unavailable'}
                </span>
              </div>
            ))}
          </div>
          
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
            These integrations enhance your AI Avatar Video Generator with additional capabilities.
          </p>
        </div>
      )}
    </div>
  );
}
