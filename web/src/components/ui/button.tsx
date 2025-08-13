import { cn } from '@/lib/utils';
import { ButtonHTMLAttributes, forwardRef } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'destructive' | 'outline' | 'ghost' | 'link';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, children, variant = 'default', size = 'md', isLoading = false, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(
          'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
          
          // Variants
          variant === 'default' && 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600',
          variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800',
          variant === 'destructive' && 'bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800',
          variant === 'outline' && 'border border-gray-300 bg-transparent hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800',
          variant === 'ghost' && 'bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800 dark:text-gray-100 dark:hover:text-gray-100',
          variant === 'link' && 'bg-transparent underline-offset-4 hover:underline text-blue-600 dark:text-blue-500 hover:bg-transparent dark:hover:bg-transparent',
          
          // Sizes
          size === 'sm' && 'h-8 px-3 text-xs',
          size === 'md' && 'h-10 py-2 px-4',
          size === 'lg' && 'h-12 px-8 text-lg',
          size === 'icon' && 'h-10 w-10',
          
          className
        )}
        ref={ref}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-gray-200 border-t-blue-600"></span>
        ) : null}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button, type ButtonProps };
