import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { InventorySession } from '../types';
import {
  ClipboardList,
  Play,
  CheckCircle2,
  AlertTriangle,
  Radio,
  Search,
  Layers,
  ArrowRight,
  Sparkles,
  MapPin
} from 'lucide-react';

export const InventoryPage: React.FC = () => {
  const [sessions, setSessions] = useState<InventorySession[]>([]);
  const [activeSession, setActiveSession] = useState<any | null>(null);
  const [scanning, setScanning] = useState(false);
  const [targetShelf, setTargetShelf] = useState('SHELF-COM-01');

  const fetchSessions = async () => {
    try {
      const data = await apiService.getInventorySessions();
      setSessions(data);
      if (data.length > 0 && !activeSession) {
        loadSessionDetail(data[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadSessionDetail = async (id: number) => {
    try {
      const detail = await apiService.getInventoryResults(id);
      setActiveSession(detail);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleStartSession = async () => {
    try {
      const newSession = await apiService.startInventory({
        session_name: `Audit - ${targetShelf} (${new Date().toLocaleTimeString()})`,
        target_shelf: targetShelf,
      });
      await fetchSessions();
      await loadSessionDetail(newSession.id);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start inventory session');
    }
  };

  const handleSimulateHandheldSweep = async () => {
    if (!activeSession) return;
    setScanning(true);
    try {
      // Simulate sweeps of tags with handheld reader
      const simulatedReads = [
        { epc: 'E20034120123456789010001', detected_shelf: targetShelf },
        { epc: 'E20034120123456789010002', detected_shelf: targetShelf },
        { epc: 'E20034120123456789010007', detected_shelf: targetShelf }, // Misplaced item from ARCHITECTURE shelf!
      ];

      for (const item of simulatedReads) {
        await apiService.scanInventoryItem({
          session_id: activeSession.id,
          epc: item.epc,
          detected_shelf: item.detected_shelf,
        });
      }

      // Mark session complete
      await apiService.completeInventory(activeSession.id);
      await loadSessionDetail(activeSession.id);
      await fetchSessions();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Handheld sweep error');
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Handheld RFID Inventory Audit (AC 05)</h1>
          <p className="text-sm text-slate-400">Rapid shelf-reading simulation, misplaced title detection, and inventory reconciliation</p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={targetShelf}
            onChange={(e) => setTargetShelf(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono"
          >
            <option value="SHELF-COM-01">Shelf: SHELF-COM-01 (Computer Science)</option>
            <option value="SHELF-REF-01">Shelf: SHELF-REF-01 (Reference)</option>
            <option value="SHELF-ARC-01">Shelf: SHELF-ARC-01 (Architecture)</option>
          </select>

          <button
            onClick={handleStartSession}
            className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow-md shadow-blue-600/20"
          >
            <Play className="w-4 h-4" />
            <span>New Shelf Session</span>
          </button>
        </div>
      </div>

      {/* Active Session Control Panel */}
      {activeSession ? (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
          <div className="flex flex-col md:flex-row justify-between md:items-center pb-4 border-b border-slate-850 gap-4">
            <div>
              <span className="text-xs uppercase tracking-wider text-slate-500 font-bold">Selected Session</span>
              <h2 className="text-lg font-bold text-white mt-0.5">{activeSession.session_name}</h2>
              <p className="text-xs text-slate-400">Target Shelf: <span className="font-mono text-cyan-400">{activeSession.target_shelf}</span></p>
            </div>

            <div className="flex items-center space-x-3">
              <span
                className={`text-xs px-3 py-1 rounded-full font-semibold border ${
                  activeSession.status === 'COMPLETED'
                    ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                    : 'bg-blue-950/80 text-blue-300 border-blue-800 animate-pulse'
                }`}
              >
                Status: {activeSession.status}
              </span>

              {activeSession.status === 'ACTIVE' && (
                <button
                  onClick={handleSimulateHandheldSweep}
                  disabled={scanning}
                  className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg shadow-indigo-600/20 disabled:opacity-50"
                >
                  <Radio className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
                  <span>{scanning ? 'Simulating RFID Sweep...' : 'Simulate Handheld Sweep (AC 05)'}</span>
                </button>
              )}
            </div>
          </div>

          {/* Session Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-xs text-slate-400">Total Scanned Copies</span>
              <div className="text-2xl font-bold text-white mt-1">{activeSession.total_scanned}</div>
            </div>
            <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-900/50">
              <span className="text-xs text-amber-400 font-medium">Misplaced on Other Shelves</span>
              <div className="text-2xl font-bold text-amber-300 mt-1">{activeSession.misplaced_count}</div>
            </div>
            <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-900/50">
              <span className="text-xs text-rose-400 font-medium">Missing Books from Shelf</span>
              <div className="text-2xl font-bold text-rose-300 mt-1">{activeSession.missing_count}</div>
            </div>
          </div>

          {/* Misplaced & Detected Items Table */}
          <div>
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
              Tag Reads Recorded by Handheld Reader
            </h3>
            <div className="overflow-x-auto border border-slate-800 rounded-lg">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/80 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">EPC</th>
                    <th className="px-4 py-3">Book Title</th>
                    <th className="px-4 py-3">Accession #</th>
                    <th className="px-4 py-3">Detected Location</th>
                    <th className="px-4 py-3">Expected Location</th>
                    <th className="px-4 py-3">Audit Outcome</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  {(activeSession.reads ?? []).length > 0 ? (
                    activeSession.reads.map((r: any) => (
                      <tr key={r.id} className="hover:bg-slate-900/40 transition">
                        <td className="px-4 py-3 font-mono text-xs text-cyan-400">{r.epc}</td>
                        <td className="px-4 py-3 font-medium text-white">{r.book_title || 'Unknown Title'}</td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-300">{r.accession_number || '-'}</td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-400">{r.detected_shelf}</td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-400">{r.expected_shelf || '-'}</td>
                        <td className="px-4 py-3">
                          {r.is_misplaced ? (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-950 text-amber-400 border border-amber-800">
                              <AlertTriangle className="w-3 h-3" />
                              <span>Misplaced Shelf!</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Correct Location</span>
                            </span>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-xs text-slate-500">
                        No RFID tag reads recorded yet in this session. Click "Simulate Handheld Sweep".
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Missing Books Section */}
          {(activeSession.missing_items ?? []).length > 0 && (
            <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-900/60">
              <h4 className="text-xs font-bold text-rose-300 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Unaccounted Copies Expected on Shelf ({activeSession.missing_items.length})</span>
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                {activeSession.missing_items.map((m: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 flex justify-between items-center">
                    <div>
                      <div className="text-sm font-semibold text-white">{m.book_title}</div>
                      <div className="text-xs font-mono text-slate-400">Acc: {m.accession_number}</div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-950 text-rose-300 border border-rose-800">
                      MISSING
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="p-12 text-center text-slate-500 bg-slate-950 border border-slate-800 rounded-xl">
          No inventory session selected. Start a new session above.
        </div>
      )}
    </div>
  );
};

