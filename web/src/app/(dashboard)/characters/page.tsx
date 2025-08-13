'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '@/store/app-store';
import { CharacterCard } from '@/components/characters/character-card';
import { AddCharacterForm } from '@/components/characters/add-character-form';
import { Button } from '@/components/ui/button';

export default function CharactersPage() {
  const { characters, fetchCharacters, selectedCharacters, toggleCharacterSelection, clearSelectedCharacters } = useAppStore();
  const [showAddForm, setShowAddForm] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [editingCharacter, setEditingCharacter] = useState(null);
  
  useEffect(() => {
    const loadData = async () => {
      await fetchCharacters();
      setIsLoading(false);
    };
    
    loadData();
  }, [fetchCharacters]);
  
  const handleCharacterSelect = (id: number) => {
    toggleCharacterSelection(id);
  };
  
  const handleEditCharacter = (character) => {
    setEditingCharacter(character);
    // Open edit modal or form
  };
  
  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Characters</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Manage your characters for video generation
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {selectedCharacters.length > 0 && (
            <Button 
              variant="outline" 
              onClick={clearSelectedCharacters}
              className="whitespace-nowrap"
            >
              Clear Selection ({selectedCharacters.length})
            </Button>
          )}
          
          <Button 
            variant={showAddForm ? 'outline' : 'primary'} 
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? 'Cancel' : 'Add Character'}
          </Button>
        </div>
      </div>
      
      {showAddForm && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Add New Character</h2>
          <AddCharacterForm onSuccess={() => setShowAddForm(false)} />
        </div>
      )}
      
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : characters.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No characters yet</h3>
          <p className="mt-1 text-gray-500 dark:text-gray-400">
            Get started by adding your first character
          </p>
          {!showAddForm && (
            <Button 
              variant="primary" 
              onClick={() => setShowAddForm(true)}
              className="mt-4"
            >
              Add Character
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {characters.map(character => (
            <CharacterCard
              key={character.id}
              character={character}
              onSelect={handleCharacterSelect}
              onEdit={handleEditCharacter}
              isSelected={selectedCharacters.includes(character.id)}
            />
          ))}
        </div>
      )}
      
      {/* Edit character modal/form would go here */}
    </div>
  );
}
