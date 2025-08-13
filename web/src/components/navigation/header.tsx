"use client";

import Link from 'next/link';
import { MainNav } from './main-nav';
import { SystemStatus } from '../system/system-status';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
      <div className="container flex h-16 items-center px-4 sm:px-8">
        <Link href="/" className="mr-6 flex items-center space-x-2">
          <span className="hidden sm:inline-block text-xl font-bold tracking-tight">
            AI Avatar Video Generator
          </span>
          <span className="sm:hidden text-xl font-bold tracking-tight">AI Gen</span>
        </Link>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="w-full flex-1 md:w-auto md:flex-none">
            <MainNav />
          </div>
          <div className="flex items-center space-x-2">
            <SystemStatus />
          </div>
        </div>
      </div>
    </header>
  );
}
