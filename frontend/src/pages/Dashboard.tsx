import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { DashboardStats } from '../types';
import {
  BookOpen,
  CheckCircle2,
  Clock,
  Users,
  Radio,
  AlertTriangle,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Link } from 'react-router-dom';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await apiService.getDashboardStats();
      setStats(data);
    } catch (e) {
      console.error('Failed to load dashboard stats', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-500 mr-2" />
        <span>Loading library operations dashboard...</span>
      </div>
    );
  }

  const statCards = [
    { label: 'Total Physical Copies', value: stats?.total_books ?? 0, icon: BookOpen, color: 'text-blue-400', bg: 'bg-blue-950/40 border-blue-800/40' },
    { label: 'Available on Shelf', value: stats?.available_books ?? 0, icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-950/40 border-emerald-800/40' },
    { label: 'Currently Issued', value: stats?.issued_books ?? 0, icon: Clock, color: 'text-amber-400', bg: 'bg-amber-950/40 border-amber-800/40' },
    { label: 'Registered Members', value: stats?.registered_members ?? 0, icon: Users, color: 'text-indigo-400', bg: 'bg-indigo-950/40 border-indigo-800/40' },
    { label: 'RFID-Tagged Items', value: stats?.rfid_tagged_items ?? 0, icon: Radio, color: 'text-cyan-400', bg: 'bg-cyan-950/40 border-cyan-800/40' },
    { label: 'Active Fines', value: `$${stats?.total_unpaid_fines ?? 0}`, sub: `${stats?.active_fines_count ?? 0} unpaid`, icon: AlertTriangle, color: 'text-rose-400', bg: 'bg-rose-950/40 border-rose-800/40' },
    { label: "Today's Transactions", value: stats?.today_transactions_count ?? 0, icon: TrendingUp, color: 'text-purple-400', bg: 'bg-purple-950/40 border-purple-800/40' },
    { label: 'Security Gate Alerts', value: stats?.unresolved_gate_alerts_count ?? 0, sub: 'Needs review', icon: ShieldAlert, color: 'text-red-400', bg: 'bg-red-950/40 border-red-800/40' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Library Operations Control</h1>
          <p className="text-sm text-slate-400">Integrated RFID circulation, inventory status, and perimeter monitoring</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadData}
            className="flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Telemetry</span>
          </button>
          <Link
            to="/circulation"
            className="flex items-center space-x-1.5 text-xs bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition shadow-md shadow-blue-600/20"
          >
            <span>Circulation Desk</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* 8 Primary Telemetry Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <div key={i} className={`p-4 rounded-xl border ${card.bg} transition hover:border-slate-700`}>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-medium text-slate-400">{card.label}</p>
                <p className="text-2xl font-bold text-white mt-1">{card.value}</p>
                {card.sub && <p className="text-[11px] text-slate-500 mt-0.5">{card.sub}</p>}
              </div>
              <div className={`p-2 rounded-lg bg-slate-900/80 border border-slate-800 ${card.color}`}>
                <card.icon className="w-5 h-5" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Visual Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Circulation Trend */}
        <div className="lg:col-span-2 bg-slate-950 border border-slate-800/80 rounded-xl p-5 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Daily Circulation Velocity</h3>
              <p className="text-xs text-slate-400">Total volume of issues and renewals over the last 7 days</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.daily_circulation_trend ?? []}>
                <XAxis dataKey="day" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                  cursor={{ fill: 'rgba(51, 65, 85, 0.3)' }}
                />
                <Bar dataKey="checkouts" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Distribution */}
        <div className="bg-slate-950 border border-slate-800/80 rounded-xl p-5 shadow-sm flex flex-col">
          <h3 className="text-sm font-semibold text-white mb-1">Catalog by Category</h3>
          <p className="text-xs text-slate-400 mb-4">Distribution of bibliographic titles</p>
          <div className="flex-1 h-52 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.category_distribution ?? []}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {(stats?.category_distribution ?? []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-900 text-[11px]">
            {(stats?.category_distribution ?? []).map((entry, idx) => (
              <div key={idx} className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                <span className="text-slate-300 truncate">{entry.name}</span>
                <span className="text-slate-500 font-mono">({entry.value})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Transactions Activity */}
      <div className="bg-slate-950 border border-slate-800/80 rounded-xl p-5 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Recent Circulation Transactions</h3>
            <p className="text-xs text-slate-400">Live operational ledger recorded with operator identity</p>
          </div>
          <Link to="/circulation" className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1">
            <span>View All</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/60 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Transaction ID</th>
                <th className="px-4 py-3">Book Title</th>
                <th className="px-4 py-3">Member</th>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {(stats?.recent_transactions ?? []).length > 0 ? (
                stats?.recent_transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">TX-{tx.id.toString().padStart(5, '0')}</td>
                    <td className="px-4 py-3 font-medium text-white">{tx.book_title}</td>
                    <td className="px-4 py-3 text-slate-300">{tx.member_name}</td>
                    <td className="px-4 py-3 text-xs text-slate-400 font-mono">{tx.date}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          tx.status === 'ISSUED'
                            ? 'bg-amber-950/60 text-amber-400 border border-amber-800/50'
                            : 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/50'
                        }`}
                      >
                        {tx.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-xs text-slate-500">
                    No transactions recorded today. Use the Circulation Desk to issue or return books.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
