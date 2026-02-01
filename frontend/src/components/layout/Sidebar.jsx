import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Video, LayoutDashboard, Plus, Library, BarChart3, Users, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Create Video', href: '/create', icon: Plus },
  { name: 'Video Library', href: '/videos', icon: Library },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Accounts', href: '/accounts', icon: Users },
  { name: 'Settings', href: '/settings', icon: Settings },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800" data-testid="sidebar">
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Video className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">AutoShorts AI</h1>
            <p className="text-xs text-slate-400">Video Automation</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              )}
              data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar;