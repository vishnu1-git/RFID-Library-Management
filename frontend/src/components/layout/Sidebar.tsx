import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  Users,
  ArrowLeftRight,
  Radio,
  ClipboardList,
  ShieldAlert,
  FileSpreadsheet,
  BarChart3,
  ShieldCheck,
  Settings,
  Layers
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Books Catalogue', path: '/books', icon: BookOpen },
  { name: 'Members', path: '/members', icon: Users },
  { name: 'Circulation', path: '/circulation', icon: ArrowLeftRight },
  { name: 'RFID Tagging', path: '/rfid', icon: Radio },
  { name: 'Shelf Inventory', path: '/inventory', icon: ClipboardList },
  { name: 'Security Gates', path: '/gates', icon: ShieldAlert },
  { name: 'Data Migration', path: '/migration', icon: FileSpreadsheet },
  { name: 'Reports & Analytics', path: '/reports', icon: BarChart3 },
  { name: 'Administration', path: '/admin', icon: ShieldCheck },
  { name: 'System Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand logo */}
      <div className="h-16 px-6 flex items-center space-x-3 border-b border-slate-800/80">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
          <Layers className="w-5 h-5" />
        </div>
        <div>
          <span className="text-base font-bold tracking-tight text-white block">LibraSync</span>
          <span className="text-[10px] text-slate-400 block -mt-1 font-mono">RFID ILMS v1.0</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-900 bg-slate-950/40 text-[11px] text-slate-400 space-y-1">
        <div className="flex justify-between">
          <span>Core Principle:</span>
          <span className="text-emerald-400 font-semibold">Strict ILMS Safety</span>
        </div>
        <p className="text-[10px] text-slate-400">External ILMS database read-only; operational DB synchronized.</p>
      </div>
    </aside>
  );
};

