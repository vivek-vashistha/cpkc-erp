'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  FileText, 
  FileCheck, 
  Truck, 
  Settings, 
  AlertTriangle, 
  History, 
  MessageSquare,
  Package,
  Users,
  BarChart3
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Waybills', href: '/waybills', icon: FileText },
  { name: 'Contracts', href: '/contracts', icon: FileCheck },
  { name: 'Assets', href: '/assets', icon: Truck },
  { name: 'Operations', href: '/operations', icon: Package },
  { name: 'Anomalies', href: '/anomalies', icon: AlertTriangle },
  { name: 'Audit Trail', href: '/audit', icon: History },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Chat Support', href: '/chat', icon: MessageSquare },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col bg-gray-900">
      <div className="flex h-16 shrink-0 items-center px-6">
        <div className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded bg-blue-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">CPKC</span>
          </div>
          <span className="text-white font-semibold">ERP Portal</span>
        </div>
      </div>
      <nav className="flex flex-1 flex-col px-3 py-4">
        <ul role="list" className="flex flex-1 flex-col gap-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    'group flex gap-x-3 rounded-md p-3 text-sm leading-6 font-semibold transition-colors',
                    isActive
                      ? 'bg-gray-800 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  )}
                >
                  <item.icon
                    className={cn(
                      'h-6 w-6 shrink-0',
                      isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}
