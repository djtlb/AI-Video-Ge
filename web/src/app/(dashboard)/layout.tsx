"use client";

import { Header } from '@/components/navigation/header';
import { Toaster } from 'sonner';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <div className="container py-6 md:py-8 px-4 sm:px-8">
          {children}
        </div>
      </main>
      <Toaster position="top-right" closeButton richColors />
    </div>
  );
}
