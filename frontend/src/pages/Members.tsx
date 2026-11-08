import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Member } from '../types';
import {
  Users,
  Search,
  Plus,
  CreditCard,
  AlertOctagon,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldAlert
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const Members: React.FC = () => {
  const { hasRole } = useAuth();
  const [members, setMembers] = useState<Member[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form state
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [dept, setDept] = useState('Computer Science');
  const [cardUid, setCardUid] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchMembers = async (query?: string) => {
    setLoading(true);
    try {
      const data = await apiService.getMembers(query);
      setMembers(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMembers(search);
  }, [search]);

  const handleStatusChange = async (memberId: number, currentStatus: string) => {
    const nextStatus = currentStatus === 'ACTIVE' ? 'BLOCKED' : 'ACTIVE';
    try {
      await apiService.updateMemberStatus(memberId, nextStatus);
      fetchMembers(search);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update member status');
    }
  };

  const handleCreateMember = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiService.createMember({
        member_code: code,
        full_name: name,
        email,
        phone,
        department: dept,
        card_rfid_uid: cardUid || undefined,
        max_borrow_limit: 4,
      });
      setShowAddModal(false);
      setCode('');
      setName('');
      setEmail('');
      setPhone('');
      setCardUid('');
      fetchMembers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to register member');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Member Registry & RFID Badges</h1>
          <p className="text-sm text-slate-400">Manage patron privileges, borrowing status, and contactless cards</p>
        </div>

        {hasRole('Librarian') && (
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow-md shadow-blue-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>Register New Member</span>
          </button>
        )}
      </div>

      {/* Search */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex items-center space-x-3">
        <Search className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search members by name, code, department, or email..."
          className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
        />
        {search && (
          <button onClick={() => setSearch('')} className="text-xs text-slate-400 hover:text-white px-2">
            Clear
          </button>
        )}
      </div>

      {/* Table */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/70 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3.5">Member Code</th>
                <th className="px-4 py-3.5">Full Name & Dept</th>
                <th className="px-4 py-3.5">Contact Details</th>
                <th className="px-4 py-3.5">Smart Card UID</th>
                <th className="px-4 py-3.5">Outstanding Fines</th>
                <th className="px-4 py-3.5">Status & Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {members.length > 0 ? (
                members.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3.5 font-mono text-xs font-bold text-white">{m.member_code}</td>
                    <td className="px-4 py-3.5">
                      <div className="font-semibold text-white">{m.full_name}</div>
                      <div className="text-xs text-slate-400">{m.department || 'General'}</div>
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="text-xs text-slate-300">{m.email}</div>
                      <div className="text-xs text-slate-500 font-mono">{m.phone || 'No phone'}</div>
                    </td>
                    <td className="px-4 py-3.5">
                      {m.card_rfid_uid ? (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono bg-indigo-950/60 text-indigo-300 border border-indigo-800/60">
                          <CreditCard className="w-3 h-3 text-indigo-400" />
                          <span>{m.card_rfid_uid}</span>
                        </span>
                      ) : (
                        <span className="text-xs text-slate-500 italic">No Smart Card</span>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      {m.outstanding_fines > 0 ? (
                        <span className="text-xs font-bold text-rose-400 font-mono">
                          ${m.outstanding_fines.toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-xs text-emerald-400 font-medium">Clear</span>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            m.status === 'ACTIVE'
                              ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                              : m.status === 'BLOCKED'
                              ? 'bg-rose-950 text-rose-400 border border-rose-800'
                              : 'bg-slate-800 text-slate-400 border border-slate-700'
                          }`}
                        >
                          {m.status === 'ACTIVE' && <CheckCircle2 className="w-3 h-3" />}
                          {m.status === 'BLOCKED' && <AlertOctagon className="w-3 h-3" />}
                          <span>{m.status}</span>
                        </span>

                        {hasRole('Librarian') && (
                          <button
                            onClick={() => handleStatusChange(m.id, m.status)}
                            className="text-[11px] underline text-slate-400 hover:text-white"
                            title="Toggle Block/Active to test AISYS borrowing restriction"
                          >
                            {m.status === 'ACTIVE' ? 'Block (AC 04)' : 'Unblock'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-xs text-slate-500">
                    {loading ? 'Loading member records...' : 'No members found.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Member Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4">Register New Library Member</h3>
            <form onSubmit={handleCreateMember} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Member Code</label>
                  <input
                    type="text"
                    required
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="e.g. MEM-2026-050"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Patron Name"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="patron@university.edu"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Phone Number</label>
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98765 00000"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Department</label>
                  <input
                    type="text"
                    value={dept}
                    onChange={(e) => setDept(e.target.value)}
                    placeholder="e.g. Mechanical"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Contactless Smart Card UID (Optional)
                </label>
                <input
                  type="text"
                  value={cardUid}
                  onChange={(e) => setCardUid(e.target.value)}
                  placeholder="e.g. CARD-MEM-STU-050"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition disabled:opacity-50"
                >
                  {submitting ? 'Registering...' : 'Register Member'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

