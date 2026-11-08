import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { RFIDTag } from '../types';
import {
  Radio,
  Plus,
  Shield,
  ShieldAlert,
  Search,
  CheckCircle2,
  RefreshCw,
  Cpu
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const RFIDTagsPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [tags, setTags] = useState<RFIDTag[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAssociateModal, setShowAssociateModal] = useState(false);

  // Form state
  const [epc, setEpc] = useState('');
  const [accession, setAccession] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchTags = async () => {
    setLoading(true);
    try {
      const data = await apiService.getTags();
      setTags(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTags();
  }, []);

  const handleAssociate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiService.associateRFIDTag({
        epc: epc.trim(),
        accession_number: accession.trim(),
      });
      setShowAssociateModal(false);
      setEpc('');
      setAccession('');
      fetchTags();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to bind RFID tag');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">RFID Tag Management (AC 02)</h1>
          <p className="text-sm text-slate-400">Electronic Product Code (EPC) encoding, EAS security bits, and antenna telemetry</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchTags}
            className="flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Scan Reader Bus</span>
          </button>

          {hasRole('Librarian') && (
            <button
              onClick={() => setShowAssociateModal(true)}
              className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow-md shadow-blue-600/20"
            >
              <Plus className="w-4 h-4" />
              <span>Encode & Bind Tag</span>
            </button>
          )}
        </div>
      </div>

      {/* Tags Table */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/70 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3.5">EPC (Electronic Product Code)</th>
                <th className="px-4 py-3.5">Associated Book Title</th>
                <th className="px-4 py-3.5">Accession #</th>
                <th className="px-4 py-3.5">EAS Security Bit (Perimeter)</th>
                <th className="px-4 py-3.5">Last Detected Reader</th>
                <th className="px-4 py-3.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {tags.length > 0 ? (
                tags.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3.5 font-mono text-xs font-bold text-cyan-400 flex items-center space-x-2">
                      <Radio className="w-3.5 h-3.5 shrink-0 text-cyan-500" />
                      <span>{t.epc}</span>
                    </td>
                    <td className="px-4 py-3.5 font-medium text-white">{t.book_title || 'Unassigned / Blank Tag'}</td>
                    <td className="px-4 py-3.5 font-mono text-xs text-slate-300">{t.accession_number || '-'}</td>
                    <td className="px-4 py-3.5">
                      {t.security_bit ? (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-950/70 text-rose-400 border border-rose-800">
                          <ShieldAlert className="w-3 h-3" />
                          <span>ARMED (In Library)</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-950/70 text-emerald-400 border border-emerald-800">
                          <Shield className="w-3 h-3" />
                          <span>DISARMED (Issued)</span>
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-400 font-mono">
                      {t.last_seen_reader || 'STAFF-DESK-01'}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-950 text-blue-400 border border-blue-800">
                        ACTIVE
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-xs text-slate-500">
                    {loading ? 'Scanning tags...' : 'No active RFID tags found.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Encode & Bind Modal */}
      {showAssociateModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center space-x-2.5 text-cyan-400 mb-4">
              <Cpu className="w-6 h-6" />
              <h3 className="text-lg font-bold text-white">Encode RFID Tag (AC 02)</h3>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Associates a physical UHF Gen 2 RFID EPC to a unique book copy accession number.
            </p>

            <form onSubmit={handleAssociate} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  RFID Electronic Product Code (EPC)
                </label>
                <input
                  type="text"
                  required
                  value={epc}
                  onChange={(e) => setEpc(e.target.value)}
                  placeholder="e.g. E20034120123456789019999"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-cyan-300 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Book Copy Accession Number
                </label>
                <input
                  type="text"
                  required
                  value={accession}
                  onChange={(e) => setAccession(e.target.value)}
                  placeholder="e.g. ACC-1252-01"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAssociateModal(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition disabled:opacity-50"
                >
                  {submitting ? 'Writing to Tag...' : 'Bind Tag to Copy'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
