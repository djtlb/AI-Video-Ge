import { cn } from '@/lib/utils';
import { InputHTMLAttributes, forwardRef } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, description, error, ...props }, ref) => {
    return (
      <div className="w-full space-y-1">
        {label && (
          <label
            className="text-sm font-medium leading-none text-gray-700 dark:text-gray-300"
            htmlFor={props.id}
          >
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-50 dark:placeholder-gray-400",
            error && "border-red-500 focus:ring-red-400",
            className
          )}
          ref={ref}
          {...props}
        />
        {description && !error && (
          <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
        )}
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

export { Input };
