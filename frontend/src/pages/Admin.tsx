import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { User } from '../types';
import {
  ShieldCheck,
  UserPlus,
  Shield,
  CreditCard,
  FileText,
  Activity,
  Search,
  Lock
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const AdminPage: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'users' | 'audit'>('users');
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [u, a] = await Promise.all([
        apiService.getUsers(),
        apiService.getAuditLogs(),
      ]);
      setUsers(u);
      setAuditLogs(a);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">System Administration & Audit (AC 07)</h1>
          <p className="text-sm text-slate-400">Staff role-based access control, smart card bindings, and forensic audit logs</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-1">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeTab === 'users'
              ? 'border-blue-500 text-blue-400 bg-slate-900/40'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Shield className="w-4 h-4" />
          <span>Staff Accounts & Roles</span>
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeTab === 'audit'
              ? 'border-blue-500 text-blue-400 bg-slate-900/40'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>System Audit Trail</span>
        </button>
      </div>

      {activeTab === 'users' && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-white">Authorized Library Staff Directory</h3>
            <span className="text-xs text-slate-400 font-mono">{users.length} Active Accounts</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/70 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3.5">Staff Member</th>
                  <th className="px-4 py-3.5">Username</th>
                  <th className="px-4 py-3.5">Assigned Roles</th>
                  <th className="px-4 py-3.5">Smart Card UID</th>
                  <th className="px-4 py-3.5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3.5">
                      <div className="font-semibold text-white">{u.full_name}</div>
                      <div className="text-xs text-slate-400">{u.email}</div>
                    </td>
                    <td className="px-4 py-3.5 font-mono text-xs text-slate-300">{u.username}</td>
                    <td className="px-4 py-3.5">
                      <div className="flex space-x-1.5">
                        {u.roles.map((r) => (
                          <span
                            key={r}
                            className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                              r === 'Admin'
                                ? 'bg-indigo-950 text-indigo-400 border-indigo-800'
                                : 'bg-emerald-950 text-emerald-400 border-emerald-800'
                            }`}
                          >
                            {r}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3.5 font-mono text-xs">
                      {u.smart_card_uid ? (
                        <span className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-indigo-300 text-[11px]">
                          <CreditCard className="w-3 h-3 text-indigo-400" />
                          <span>{u.smart_card_uid}</span>
                        </span>
                      ) : (
                        <span className="text-slate-500 italic">None</span>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                        Active
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-white">Immutable Operational Audit Log</h3>
            <span className="text-xs text-slate-400 font-mono">Real-time ledger</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/70 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3.5">Timestamp</th>
                  <th className="px-4 py-3.5">Operator</th>
                  <th className="px-4 py-3.5">Action Executed</th>
                  <th className="px-4 py-3.5">Entity</th>
                  <th className="px-4 py-3.5">Audit Payload Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3.5 text-xs text-slate-400 font-mono">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-3.5 font-medium text-white">{log.username || 'System Daemon'}</td>
                    <td className="px-4 py-3.5">
                      <span className="text-xs font-mono font-bold text-blue-400">{log.action}</span>
                    </td>
                    <td className="px-4 py-3.5 text-xs font-mono text-slate-300">
                      {log.entity_type} {log.entity_id ? `(${log.entity_id})` : ''}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-400 font-mono truncate max-w-xs" title={log.details}>
                      {log.details || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

