import Image from 'next/image';
import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { useAppStore, type Character } from '@/store/app-store';
import { getImageUrlFromPath } from '@/lib/utils';
import { api } from '@/services/api';

interface CharacterCardProps {
  character: Character;
  onSelect: (id: number) => void;
  onEdit: (character: Character) => void;
  isSelected: boolean;
}

export function CharacterCard({ character, onSelect, onEdit, isSelected }: CharacterCardProps) {
  const { deleteCharacter } = useAppStore();
  const [isDeleting, setIsDeleting] = useState(false);
  const [isEnhancing, setIsEnhancing] = useState(false);
  
  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card selection when clicking delete
    
    if (confirm(`Are you sure you want to delete "${character.name}"?`)) {
      setIsDeleting(true);
      try {
        await deleteCharacter(character.id);
        toast.success(`${character.name} deleted successfully`);
      } catch (error) {
        toast.error(`Failed to delete ${character.name}`);
        console.error(error);
      } finally {
        setIsDeleting(false);
      }
    }
  };
  
  const handleEnhance = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card selection
    
    setIsEnhancing(true);
    toast.info(`Enhancing ${character.name}...`);
    
    try {
      const prompt = prompt("Enter an optional enhancement prompt (or leave empty):");
      await api.enhancePortrait(character.id, prompt || undefined);
      toast.success(`${character.name} enhanced successfully`);
      // Refresh characters list
      await useAppStore.getState().fetchCharacters();
    } catch (error) {
      toast.error(`Failed to enhance ${character.name}`);
      console.error(error);
    } finally {
      setIsEnhancing(false);
    }
  };
  
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card selection
    onEdit(character);
  };

  // Get image URL from path
  const imageUrl = getImageUrlFromPath(character.thumb_path);
  
  // Check if character has been enhanced
  const isEnhanced = character.meta && character.meta.enhanced;
  
  return (
    <div 
      className={`
        relative rounded-lg overflow-hidden cursor-pointer transition-all duration-200
        ${isSelected ? 'ring-2 ring-blue-500 dark:ring-blue-400 scale-[1.02]' : 'hover:scale-[1.01]'}
        bg-white dark:bg-gray-800 shadow-sm hover:shadow-md
      `}
      onClick={() => onSelect(character.id)}
    >
      <div className="aspect-square relative">
        <Image
          src={imageUrl}
          alt={character.name}
          fill
          className="object-contain"
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />
        
        {/* Selection indicator */}
        {isSelected && (
          <div className="absolute top-2 right-2 bg-blue-500 rounded-full h-6 w-6 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-white">
              <path fillRule="evenodd" d="M19.916 4.626a.75.75 0 01.208 1.04l-9 13.5a.75.75 0 01-1.154.114l-6-6a.75.75 0 011.06-1.06l5.353 5.353 8.493-12.739a.75.75 0 011.04-.208z" clipRule="evenodd" />
            </svg>
          </div>
        )}
        
        {/* Enhanced badge */}
        {isEnhanced && (
          <div className="absolute top-2 left-2 bg-purple-500 text-white text-xs font-medium px-2 py-1 rounded-full">
            Enhanced
          </div>
        )}
      </div>
      
      <div className="p-3">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 truncate">{character.name}</h3>
        
        <div className="mt-3 flex space-x-2">
          <Button 
            size="sm" 
            variant="outline" 
            className="flex-1"
            onClick={handleEdit}
          >
            Edit
          </Button>
          
          <Button 
            size="sm" 
            variant="outline" 
            className="flex-1"
            onClick={handleEnhance}
            isLoading={isEnhancing}
            disabled={isEnhancing}
          >
            Enhance
          </Button>
          
          <Button 
            size="sm" 
            variant="destructive" 
            className="w-8 p-0" 
            onClick={handleDelete}
            isLoading={isDeleting}
            disabled={isDeleting}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
              <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clipRule="evenodd" />
            </svg>
          </Button>
        </div>
      </div>
    </div>
  );
}
