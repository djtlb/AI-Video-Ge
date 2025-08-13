import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { FileUpload } from '@/components/ui/file-upload';
import { useAppStore } from '@/store/app-store';

interface AddCharacterFormProps {
  onSuccess?: () => void;
}

export function AddCharacterForm({ onSuccess }: AddCharacterFormProps) {
  const { addCharacter } = useAppStore();
  const [name, setName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!name.trim()) {
      setError('Please enter a character name');
      return;
    }
    
    if (!file) {
      setError('Please upload an image');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('file', file);
      
      await addCharacter(formData);
      
      // Reset form
      setName('');
      setFile(null);
      
      toast.success('Character added successfully');
      
      // Call success callback if provided
      onSuccess?.();
    } catch (error) {
      console.error('Error adding character:', error);
      setError(error instanceof Error ? error.message : 'Failed to add character');
      toast.error('Failed to add character');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Input
        label="Character Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter character name"
        disabled={isLoading}
        error={!name.trim() && error ? 'Please enter a character name' : undefined}
      />
      
      <FileUpload
        label="Character Image"
        onFileSelect={(selectedFile) => setFile(selectedFile)}
        accept={{ 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] }}
        maxSize={5 * 1024 * 1024} // 5MB
        error={!file && error ? 'Please upload an image' : undefined}
      />
      
      {error && !error.includes('name') && !error.includes('image') && (
        <p className="text-sm text-red-500">{error}</p>
      )}
      
      <div className="flex justify-end">
        <Button
          type="submit"
          variant="primary"
          isLoading={isLoading}
          disabled={isLoading}
        >
          Add Character
        </Button>
      </div>
    </form>
  );
}
