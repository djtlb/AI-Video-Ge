import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navigationItems = [
  { name: 'Characters', href: '/characters' },
  { name: 'Video Generation', href: '/generate' },
  { name: 'Gallery', href: '/gallery' },
  { name: 'AI Integrations', href: '/integrations' },
  { name: 'Settings', href: '/settings' },
];

export function MainNav() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center space-x-6 text-sm font-medium">
      {navigationItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            'transition-colors hover:text-foreground/80',
            pathname === item.href || pathname.startsWith(`${item.href}/`)
              ? 'text-blue-600 dark:text-blue-400 font-semibold'
              : 'text-gray-600 dark:text-gray-400'
          )}
        >
          {item.name}
        </Link>
      ))}
    </nav>
  );
}
