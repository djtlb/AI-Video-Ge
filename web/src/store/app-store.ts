import { create } from 'zustand';
import { api } from '@/services/api';

export interface Character {
  id: number;
  name: string;
  original_path: string;
  cutout_path: string;
  thumb_path: string;
  edited_path?: string;
  meta?: any;
  scale?: number;
  rotation?: number;
  brightness?: number;
  contrast?: number;
  fixed_position?: boolean;
  move_range?: number;
  breathe_amount?: number;
  breathe_speed?: number;
  tilt_factor?: number;
  path_type?: string;
}

export interface Video {
  video_path: string;
  name: string;
  created_at: string;
}

export interface SystemInfo {
  gpu: {
    available: boolean;
    model: string;
    memory: string;
    isAmd: boolean;
  };
  cpu: string;
  memory: string;
  os: string;
}

interface IntegrationsStatus {
  available: boolean;
  initialized: boolean;
  modules: {
    facechain: boolean;
    talking_avatar: boolean;
    comfyui: boolean;
    stable_diffusion: boolean;
    avatar3d: boolean;
    image_generator: boolean;
  };
}

interface AppState {
  characters: Character[];
  videos: Video[];
  selectedCharacters: number[];
  systemInfo: SystemInfo;
  isLoading: boolean;
  integrations: IntegrationsStatus;
  error: string | null;
  
  // Actions
  fetchCharacters: () => Promise<void>;
  fetchVideos: () => Promise<void>;
  fetchSystemInfo: () => Promise<void>;
  fetchIntegrationsStatus: () => Promise<void>;
  addCharacter: (formData: FormData) => Promise<void>;
  deleteCharacter: (id: number) => Promise<void>;
  selectCharacter: (id: number) => void;
  unselectCharacter: (id: number) => void;
  toggleCharacterSelection: (id: number) => void;
  clearSelectedCharacters: () => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  characters: [],
  videos: [],
  selectedCharacters: [],
  systemInfo: {
    gpu: {
      available: false,
      model: 'Unknown',
      memory: 'Unknown',
      isAmd: false
    },
    cpu: 'Unknown',
    memory: 'Unknown',
    os: 'Unknown',
  },
  isLoading: false,
  integrations: {
    available: false,
    initialized: false,
    modules: {
      facechain: false,
      talking_avatar: false,
      comfyui: false,
      stable_diffusion: false,
      avatar3d: false,
      image_generator: false
    }
  },
  error: null,
  
  // Fetch characters from the API
  fetchCharacters: async () => {
    set({ isLoading: true, error: null });
    try {
      const characters = await api.getCharacters();
      set({ characters, isLoading: false });
    } catch (error) {
      console.error('Error fetching characters:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch characters', 
        isLoading: false 
      });
    }
  },
  
  // Fetch videos from the API
  fetchVideos: async () => {
    set({ isLoading: true, error: null });
    try {
      const videos = await api.getRenderedVideos();
      set({ videos, isLoading: false });
    } catch (error) {
      console.error('Error fetching videos:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch videos', 
        isLoading: false 
      });
    }
  },
  
  // Fetch system information
  fetchSystemInfo: async () => {
    set({ isLoading: true, error: null });
    try {
      // First check for GPU status
      const gpuStatus = await api.getGpuStatus();
      
      // Then get general system info
      const sysInfo = await api.getSystemInfo();
      
      set({ 
        systemInfo: {
          gpu: {
            available: gpuStatus.gpu_available || false,
            model: gpuStatus.gpu_model || 'Not detected',
            memory: gpuStatus.gpu_memory || 'Unknown',
            isAmd: (gpuStatus.gpu_model || '').toLowerCase().includes('amd') || 
                   (gpuStatus.gpu_type || '').toLowerCase() === 'amd'
          },
          cpu: sysInfo.cpu || 'Unknown',
          memory: sysInfo.memory || 'Unknown',
          os: sysInfo.os || 'Unknown',
        },
        isLoading: false 
      });
    } catch (error) {
      console.error('Error fetching system info:', error);
      set({ isLoading: false });
      // Don't set error since this is a background operation
    }
  },
  
  // Fetch integrations status
  fetchIntegrationsStatus: async () => {
    try {
      const status = await api.getIntegrationsStatus();
      set({ integrations: status });
    } catch (error) {
      console.error('Error fetching integrations status:', error);
      // Don't set loading or error states
    }
  },
  
  // Add a new character
  addCharacter: async (formData: FormData) => {
    set({ isLoading: true, error: null });
    try {
      await api.createCharacter(formData);
      // Refresh the character list
      await get().fetchCharacters();
    } catch (error) {
      console.error('Error adding character:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to add character', 
        isLoading: false 
      });
    }
  },
  
  // Delete a character
  deleteCharacter: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await api.deleteCharacter(id);
      // Refresh the character list
      await get().fetchCharacters();
      // Remove from selected characters if it's there
      set(state => ({
        selectedCharacters: state.selectedCharacters.filter(charId => charId !== id)
      }));
    } catch (error) {
      console.error('Error deleting character:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to delete character', 
        isLoading: false 
      });
    }
  },
  
  // Character selection helpers
  selectCharacter: (id: number) => {
    set(state => {
      if (!state.selectedCharacters.includes(id)) {
        return { selectedCharacters: [...state.selectedCharacters, id] };
      }
      return state;
    });
  },
  
  unselectCharacter: (id: number) => {
    set(state => ({
      selectedCharacters: state.selectedCharacters.filter(charId => charId !== id)
    }));
  },
  
  toggleCharacterSelection: (id: number) => {
    set(state => {
      if (state.selectedCharacters.includes(id)) {
        return {
          selectedCharacters: state.selectedCharacters.filter(charId => charId !== id)
        };
      } else {
        return {
          selectedCharacters: [...state.selectedCharacters, id]
        };
      }
    });
  },
  
  clearSelectedCharacters: () => {
    set({ selectedCharacters: [] });
  },
  
  // Error handling
  setError: (error: string | null) => {
    set({ error });
  }
}));
