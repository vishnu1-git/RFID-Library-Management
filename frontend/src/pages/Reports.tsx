import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { DashboardStats, Circulation } from '../types';
import {
  BarChart3,
  Download,
  Calendar,
  Filter,
  RefreshCw,
  BookOpen,
  ArrowUpDown,
  FileText
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [history, setHistory] = useState<Circulation[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const loadReportData = async () => {
    setLoading(true);
    try {
      const [s, h] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getCirculationHistory(),
      ]);
      setStats(s);
      setHistory(h);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReportData();
  }, []);

  const filteredHistory = history.filter((item) => {
    if (filterStatus === 'ALL') return true;
    return item.status === filterStatus;
  });

  const exportCSV = () => {
    const headers = ['Transaction ID', 'Accession #', 'Book Title', 'Member Name', 'Member Code', 'Checkout Date', 'Due Date', 'Status'];
    const rows = filteredHistory.map((h) => [
      h.id,
      h.accession_number,
      `"${h.book_title}"`,
      `"${h.member_name}"`,
      h.member_code,
      h.checkout_date,
      h.due_date,
      h.status,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `librasync_circulation_report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Reports & Analytical Insights (AC 08)</h1>
          <p className="text-sm text-slate-400">Exportable circulation ledgers, collection utilization, and member statistics</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadReportData}
            className="flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>

          <button
            onClick={exportCSV}
            className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow-md shadow-blue-600/20"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV Dataset (AC 08)</span>
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3 text-xs">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-slate-400 font-medium">Filter by Status:</span>
          <div className="flex space-x-1.5">
            {['ALL', 'ISSUED', 'RETURNED'].map((st) => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                  filterStatus === st
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        <div className="text-xs text-slate-400 font-mono">
          Showing {filteredHistory.length} ledger entries
        </div>
      </div>

      {/* Report Table */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/70 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3.5">ID</th>
                <th className="px-4 py-3.5">Accession Number</th>
                <th className="px-4 py-3.5">Title</th>
                <th className="px-4 py-3.5">Patron Name</th>
                <th className="px-4 py-3.5">Checkout Date</th>
                <th className="px-4 py-3.5">Due Date</th>
                <th className="px-4 py-3.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {filteredHistory.length > 0 ? (
                filteredHistory.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">TX-{item.id}</td>
                    <td className="px-4 py-3 font-mono text-xs font-bold text-white">{item.accession_number}</td>
                    <td className="px-4 py-3 font-medium text-white">{item.book_title}</td>
                    <td className="px-4 py-3 text-slate-300">{item.member_name}</td>
                    <td className="px-4 py-3 text-xs text-slate-400 font-mono">
                      {new Date(item.checkout_date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400 font-mono">
                      {new Date(item.due_date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                          item.status === 'ISSUED'
                            ? 'bg-amber-950 text-amber-400 border border-amber-800'
                            : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        }`}
                      >
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-xs text-slate-500">
                    No transactions match current filter.
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

