import { useState } from 'react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAppStore } from '@/store/app-store';
import { api } from '@/services/api';

interface VideoGenerationFormProps {
  onSuccess: (videoPath: string) => void;
}

interface FormValues {
  prompt: string;
  duration_seconds: number;
  width: number;
  height: number;
  fps: number;
  seed?: number;
  use_amd_gpu: boolean;
  use_comfyui: boolean;
  use_stable_diffusion: boolean;
}

export function VideoGenerationForm({ onSuccess }: VideoGenerationFormProps) {
  const { selectedCharacters, systemInfo } = useAppStore();
  const [isGenerating, setIsGenerating] = useState(false);
  
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    defaultValues: {
      prompt: '',
      duration_seconds: 15,
      width: 768,
      height: 432,
      fps: 24,
      use_amd_gpu: systemInfo.gpu.isAmd, // Default to AMD GPU if available
      use_comfyui: false,
      use_stable_diffusion: false
    }
  });
  
  const onSubmit = async (data: FormValues) => {
    if (selectedCharacters.length === 0) {
      toast.error('Please select at least one character');
      return;
    }
    
    setIsGenerating(true);
    toast.info('Generating video...');
    
    try {
      // Prepare the request data
      const requestData = {
        ...data,
        character_ids: selectedCharacters,
        // AMD GPU handling
        device: 'cuda' // ROCm/AMD uses 'cuda' device name in PyTorch
      };
      
      // Use advanced video generation if ComfyUI or Stable Diffusion is enabled
      let result;
      if (data.use_comfyui || data.use_stable_diffusion) {
        result = await api.generateAdvancedVideo({
          ...requestData,
          use_comfyui: data.use_comfyui,
          use_stable_diffusion: data.use_stable_diffusion
        });
      } else {
        result = await api.generateVideo(requestData);
      }
      
      toast.success('Video generated successfully!');
      onSuccess(result.video_path);
    } catch (error) {
      console.error('Error generating video:', error);
      toast.error('Failed to generate video');
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Selected Characters
        </label>
        <div className="text-sm bg-gray-50 dark:bg-gray-800 p-3 rounded-md">
          {selectedCharacters.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400">No characters selected. Please select characters from the Characters page.</p>
          ) : (
            <p>{selectedCharacters.length} character(s) selected</p>
          )}
        </div>
      </div>
      
      <Input
        label="Prompt"
        placeholder="Describe the scene, e.g. 'underwater city with colorful fish'"
        {...register('prompt', { required: 'Prompt is required' })}
        error={errors.prompt?.message}
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Duration (seconds)"
          type="number"
          {...register('duration_seconds', { 
            required: 'Duration is required',
            min: { value: 10, message: 'Minimum 10 seconds' },
            max: { value: 30, message: 'Maximum 30 seconds' }
          })}
          error={errors.duration_seconds?.message}
        />
        
        <Input
          label="FPS"
          type="number"
          {...register('fps', { 
            required: 'FPS is required',
            min: { value: 12, message: 'Minimum 12 FPS' },
            max: { value: 30, message: 'Maximum 30 FPS' }
          })}
          error={errors.fps?.message}
        />
        
        <Input
          label="Width"
          type="number"
          {...register('width', { 
            required: 'Width is required',
            min: { value: 512, message: 'Minimum 512px' },
            max: { value: 1024, message: 'Maximum 1024px' }
          })}
          error={errors.width?.message}
        />
        
        <Input
          label="Height"
          type="number"
          {...register('height', { 
            required: 'Height is required',
            min: { value: 512, message: 'Minimum 512px' },
            max: { value: 1024, message: 'Maximum 1024px' }
          })}
          error={errors.height?.message}
        />
        
        <Input
          label="Seed (optional)"
          type="number"
          placeholder="Leave empty for random"
          {...register('seed', { 
            valueAsNumber: true,
            validate: (value) => {
              if (value !== undefined && isNaN(value)) return 'Must be a number';
              return true;
            }
          })}
          error={errors.seed?.message}
        />
      </div>
      
      <div className="space-y-4">
        <h3 className="font-medium text-gray-900 dark:text-gray-100">Advanced Options</h3>
        
        <div className="flex items-center">
          <input
            type="checkbox"
            id="use_amd_gpu"
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4"
            {...register('use_amd_gpu')}
            disabled={!systemInfo.gpu.isAmd}
          />
          <label htmlFor="use_amd_gpu" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
            Use AMD GPU acceleration
            {!systemInfo.gpu.isAmd && (
              <span className="ml-2 text-xs text-gray-500">(No AMD GPU detected)</span>
            )}
          </label>
        </div>
        
        <div className="flex items-center">
          <input
            type="checkbox"
            id="use_comfyui"
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4"
            {...register('use_comfyui')}
          />
          <label htmlFor="use_comfyui" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
            Use ComfyUI for background generation (higher quality, slower)
          </label>
        </div>
        
        <div className="flex items-center">
          <input
            type="checkbox"
            id="use_stable_diffusion"
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4"
            {...register('use_stable_diffusion')}
          />
          <label htmlFor="use_stable_diffusion" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
            Use Stable Diffusion for background generation
          </label>
        </div>
      </div>
      
      <div className="flex justify-end">
        <Button
          type="submit"
          variant="primary"
          size="lg"
          isLoading={isGenerating}
          disabled={isGenerating || selectedCharacters.length === 0}
        >
          {isGenerating ? 'Generating...' : 'Generate Video'}
        </Button>
      </div>
    </form>
  );
}
