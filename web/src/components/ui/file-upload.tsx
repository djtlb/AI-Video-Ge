import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  label?: string;
  accept?: Record<string, string[]>;
  className?: string;
  maxSize?: number; // in bytes
  error?: string;
}

export function FileUpload({
  onFileSelect,
  label = 'Upload a file',
  accept = {
    'image/*': ['.png', '.jpg', '.jpeg', '.webp']
  },
  className,
  maxSize = 10 * 1024 * 1024, // 10MB default
  error
}: FileUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false
  });

  return (
    <div className="w-full space-y-2">
      {label && <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</p>}
      <div 
        {...getRootProps()} 
        className={cn(
          'border-2 border-dashed rounded-lg p-6 transition-colors cursor-pointer flex flex-col items-center justify-center',
          isDragActive ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-700',
          isDragReject && 'border-red-500 bg-red-50 dark:bg-red-900/20',
          error && 'border-red-500',
          className
        )}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center text-center space-y-2">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className={cn(
              "h-10 w-10",
              isDragActive ? 'text-blue-500' : 'text-gray-400',
              isDragReject && 'text-red-500'
            )} 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
            />
          </svg>
          <div className="text-gray-700 dark:text-gray-300">
            {isDragActive ? (
              <p>Drop the file here...</p>
            ) : (
              <p>Drag & drop a file here, or click to select</p>
            )}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Max size: {Math.round(maxSize / 1024 / 1024)}MB
          </p>
        </div>
      </div>
      {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
    </div>
  );
}
