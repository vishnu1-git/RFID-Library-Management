import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { GateEvent } from '../types';
import {
  ShieldAlert,
  ShieldCheck,
  Camera,
  Bell,
  RefreshCw,
  CheckCircle2,
  AlertOctagon,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const GateEventsPage: React.FC = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState<GateEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeAlert, setActiveAlert] = useState<GateEvent | null>(null);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await apiService.getGateEvents();
      setEvents(data);
      const latestUnresolvedAlarm = data.find((e) => e.alarm_triggered && !e.resolved);
      if (latestUnresolvedAlarm) {
        setActiveAlert(latestUnresolvedAlarm);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleSimulateUnauthorizedWalk = async () => {
    try {
      // EPC of Clean Code copy 1 (ARMED in library)
      const res = await apiService.triggerGateEvent({
        reader_id: 'GATE-NORTH-EXIT-01',
        epc: 'E20034120123456789010001',
      });
      setActiveAlert(res);
      fetchEvents();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Simulation error');
    }
  };

  const handleSimulateAuthorizedWalk = async () => {
    try {
      // First ensure it's checked out, or pass disarmed EPC
      const res = await apiService.triggerGateEvent({
        reader_id: 'GATE-NORTH-EXIT-01',
        epc: 'E20034120123456789010008', // Tag 8 (disarmed or valid)
      });
      fetchEvents();
      alert(`Gate Scanner: ${res.is_authorized ? 'Authorized passage' : 'Alarm triggered'}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Simulation error');
    }
  };

  const handleResolve = async (eventId: number) => {
    try {
      await apiService.resolveGateEvent(eventId, 'Verified by security staff; false alarm cleared.');
      if (activeAlert?.id === eventId) setActiveAlert(null);
      fetchEvents();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to resolve event');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Perimeter Security & RFID Gates (AC 06)</h1>
          <p className="text-sm text-slate-400">Automated EAS anti-theft gates, optical CCTV capture, and security dispatch</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchEvents}
            className="flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Poll Telemetry</span>
          </button>

          <button
            onClick={handleSimulateUnauthorizedWalk}
            className="flex items-center space-x-1.5 bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-md shadow-rose-600/30"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Simulate Alarm Passage (AC 06)</span>
          </button>

          <button
            onClick={handleSimulateAuthorizedWalk}
            className="flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-2 rounded-lg text-sm font-medium transition"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Authorized Pass</span>
          </button>
        </div>
      </div>

      {/* Live Alarm Banner if triggered */}
      {activeAlert && (
        <div className="p-6 rounded-2xl bg-rose-950/60 border-2 border-rose-600 shadow-2xl animate-pulse space-y-4">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-rose-600 text-white rounded-xl shadow-lg shadow-rose-600/40">
                <ShieldAlert className="w-8 h-8" />
              </div>
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-rose-400">
                  Critical Security Breach Detected
                </span>
                <h2 className="text-xl font-bold text-white">Unauthorized Book Removal at {activeAlert.reader_id}</h2>
                <p className="text-xs text-rose-200 mt-0.5">
                  EAS Security Bit is ARMED. Book copy <span className="font-mono font-bold text-white">{activeAlert.accession_number || activeAlert.epc}</span> has not been checked out!
                </p>
              </div>
            </div>

            <button
              onClick={() => handleResolve(activeAlert.id)}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white border border-rose-500/80 rounded-xl text-xs font-semibold transition self-start sm:self-auto shrink-0"
            >
              Acknowledge & Disarm Alarm
            </button>
          </div>

          {/* CCTV Snapshot Preview (AC 06 requirement) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-rose-900/50">
            <div className="md:col-span-1 rounded-xl overflow-hidden border border-rose-800 bg-slate-950 relative">
              <div className="absolute top-2 left-2 bg-rose-600 text-[10px] font-bold px-2 py-0.5 rounded text-white flex items-center space-x-1">
                <Camera className="w-3 h-3" />
                <span>CCTV CAMERA NORTH-01</span>
              </div>
              <img
                src={activeAlert.cctv_snapshot_url || 'https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=400&q=80'}
                alt="Security snapshot"
                className="w-full h-40 object-cover opacity-85"
              />
            </div>
            <div className="md:col-span-2 space-y-2 text-xs text-rose-200">
              <div className="flex justify-between py-1 border-b border-rose-900/40">
                <span className="text-slate-400">Target EPC:</span>
                <span className="font-mono text-white font-bold">{activeAlert.epc}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-rose-900/40">
                <span className="text-slate-400">Suspected Volume:</span>
                <span className="text-white font-semibold">{activeAlert.book_title || 'Clean Code (Acc: ACC-0884-01)'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-rose-900/40">
                <span className="text-slate-400">Automated Notification:</span>
                <span className="text-emerald-400 font-semibold">Queued to security-ops@library.local (AC 06)</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Timestamp:</span>
                <span className="font-mono text-slate-300">{new Date(activeAlert.timestamp).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Events Log Table */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-sm font-semibold text-white">Security Gate Event Log</h3>
          <span className="text-xs text-slate-400 font-mono">Antenna Gate Bus: ACTIVE</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/70 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3.5">Event ID</th>
                <th className="px-4 py-3.5">Gate Reader ID</th>
                <th className="px-4 py-3.5">Detected EPC</th>
                <th className="px-4 py-3.5">Title / Copy</th>
                <th className="px-4 py-3.5">Gate Response</th>
                <th className="px-4 py-3.5">Timestamp</th>
                <th className="px-4 py-3.5">Incident State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {events.length > 0 ? (
                events.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3.5 font-mono text-xs text-slate-400">EVT-{ev.id.toString().padStart(4, '0')}</td>
                    <td className="px-4 py-3.5 font-mono text-xs text-slate-300">{ev.reader_id}</td>
                    <td className="px-4 py-3.5 font-mono text-xs text-cyan-400">{ev.epc}</td>
                    <td className="px-4 py-3.5 font-medium text-white">{ev.book_title || ev.accession_number || 'Unknown'}</td>
                    <td className="px-4 py-3.5">
                      {ev.alarm_triggered ? (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-950 text-rose-400 border border-rose-800">
                          <AlertOctagon className="w-3 h-3" />
                          <span>ALARM TRIGGERED</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Authorized Pass</span>
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-400 font-mono">
                      {new Date(ev.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-3.5">
                      {ev.alarm_triggered ? (
                        ev.resolved ? (
                          <span className="text-xs text-slate-400 font-medium">Resolved</span>
                        ) : (
                          <button
                            onClick={() => handleResolve(ev.id)}
                            className="px-2.5 py-1 text-xs bg-rose-950 text-rose-300 border border-rose-800 rounded-md hover:bg-rose-900 transition"
                          >
                            Resolve Alert
                          </button>
                        )
                      ) : (
                        <span className="text-xs text-slate-500">-</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-xs text-slate-500">
                    {loading ? 'Polling gate events...' : 'No gate events recorded yet.'}
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

