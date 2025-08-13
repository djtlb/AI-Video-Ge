import axios from 'axios';
import { absoluteUrl } from '@/lib/utils';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service with typed responses
export const api = {
  // Character management
  async getCharacters() {
    const response = await apiClient.get('/characters');
    return response.data;
  },

  async createCharacter(formData: FormData) {
    const response = await apiClient.post('/characters', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async deleteCharacter(id: number) {
    const response = await apiClient.delete(`/characters/${id}`);
    return response.data;
  },

  async editCharacter(id: number, data: any) {
    const response = await apiClient.post(`/characters/${id}/edit`, data);
    return response.data;
  },

  // Video generation
  async generateVideo(data: any) {
    // Use specific request to ensure AMD GPU is used
    const requestData = {
      ...data,
      use_amd_gpu: true, // Force AMD GPU usage
    };
    
    const response = await apiClient.post('/generate', requestData);
    return response.data;
  },

  async getRenderedVideos() {
    const response = await apiClient.get('/renders');
    return response.data;
  },

  async editVideo(data: any) {
    const response = await apiClient.post('/edit-video', data);
    return response.data;
  },

  // Integration endpoints
  async getIntegrationsStatus() {
    const response = await apiClient.get('/integrations/status');
    return response.data;
  },

  async enhancePortrait(charId: number, prompt?: string) {
    const response = await apiClient.post('/integrations/enhance-portrait', {
      char_id: charId,
      prompt,
    });
    return response.data;
  },

  async generateTalkingAvatar(charId: number, text: string, durationSeconds: number = 10, useAdvancedMotion: boolean = true) {
    const response = await apiClient.post('/integrations/generate-talking-avatar', {
      char_id: charId,
      text,
      duration_seconds: durationSeconds,
      use_advanced_motion: useAdvancedMotion,
    });
    return response.data;
  },

  async generateAdvancedVideo(data: any) {
    // Force AMD GPU usage
    const requestData = {
      ...data,
      use_amd_gpu: true, // Explicitly request AMD GPU
      device: 'cuda', // For ROCm/AMD, PyTorch uses 'cuda' device name
    };
    
    const response = await apiClient.post('/integrations/generate-advanced-video', requestData);
    return response.data;
  },

  async generateAvatar3d(charId: number, prompt?: string) {
    const response = await apiClient.post('/integrations/avatar3d', {
      char_id: charId,
      prompt,
    });
    return response.data;
  },

  async generateAiImage(prompt: string, size: string = 'medium') {
    const response = await apiClient.post('/integrations/generate-ai-image', {
      prompt,
      size,
    });
    return response.data;
  },

  // System information
  async getGpuStatus() {
    const response = await apiClient.get('/gpu/status');
    return response.data;
  },

  async getSystemInfo() {
    const response = await apiClient.get('/system/info');
    return response.data;
  },
};

// Download helper function
export const downloadVideo = (videoPath: string) => {
  window.location.href = absoluteUrl(`/download?video_path=${videoPath}`);
};

export default api;
