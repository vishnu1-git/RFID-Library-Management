import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Circulation, Fine } from '../types';
import {
  ArrowLeftRight,
  Radio,
  CreditCard,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Clock,
  DollarSign,
  AlertOctagon,
  Sparkles,
  Search
} from 'lucide-react';

export const CirculationPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'checkout' | 'checkin' | 'renew' | 'fines' | 'active'>('checkout');
  
  // Checkout form
  const [checkoutMember, setCheckoutMember] = useState('MEM-2026-001');
  const [checkoutItem, setCheckoutItem] = useState('ACC-0884-01');
  const [checkoutResult, setCheckoutResult] = useState<any>(null);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  // Checkin form
  const [checkinItem, setCheckinItem] = useState('');
  const [checkinResult, setCheckinResult] = useState<any>(null);
  const [checkinError, setCheckinError] = useState<string | null>(null);

  // Renew form
  const [renewItem, setRenewItem] = useState('');
  const [renewResult, setRenewResult] = useState<any>(null);
  const [renewError, setRenewError] = useState<string | null>(null);

  // Lists
  const [activeLoans, setActiveLoans] = useState<Circulation[]>([]);
  const [fines, setFines] = useState<Fine[]>([]);
  const [loading, setLoading] = useState(false);

  const loadActiveLoans = async () => {
    try {
      const data = await apiService.getActiveCirculation();
      setActiveLoans(data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadFines = async () => {
    try {
      const data = await apiService.getFines();
      setFines(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (activeTab === 'active') loadActiveLoans();
    if (activeTab === 'fines') loadFines();
  }, [activeTab]);

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    setCheckoutError(null);
    setCheckoutResult(null);
    setLoading(true);
    try {
      const res = await apiService.checkout({
        member_code: checkoutMember.trim(),
        accession_number: checkoutItem.startsWith('E200') ? undefined : checkoutItem.trim(),
        epc: checkoutItem.startsWith('E200') ? checkoutItem.trim() : undefined,
      });
      setCheckoutResult(res);
      loadActiveLoans();
    } catch (err: any) {
      setCheckoutError(err.response?.data?.detail || 'Checkout transaction rejected');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckin = async (e: React.FormEvent) => {
    e.preventDefault();
    setCheckinError(null);
    setCheckinResult(null);
    setLoading(true);
    try {
      const res = await apiService.checkin({
        accession_number: checkinItem.startsWith('E200') ? undefined : checkinItem.trim(),
        epc: checkinItem.startsWith('E200') ? checkinItem.trim() : undefined,
      });
      setCheckinResult(res);
      setCheckinItem('');
      loadActiveLoans();
    } catch (err: any) {
      setCheckinError(err.response?.data?.detail || 'Check-in transaction rejected');
    } finally {
      setLoading(false);
    }
  };

  const handleRenew = async (e: React.FormEvent) => {
    e.preventDefault();
    setRenewError(null);
    setRenewResult(null);
    setLoading(true);
    try {
      const res = await apiService.renew({
        accession_number: renewItem.startsWith('E200') ? undefined : renewItem.trim(),
        epc: renewItem.startsWith('E200') ? renewItem.trim() : undefined,
      });
      setRenewResult(res);
      loadActiveLoans();
    } catch (err: any) {
      setRenewError(err.response?.data?.detail || 'Renewal transaction rejected');
    } finally {
      setLoading(false);
    }
  };

  const handleSettleFine = async (fineId: number, action: 'PAY' | 'WAIVE') => {
    try {
      await apiService.settleFine(fineId, action);
      loadFines();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Fine settlement failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Circulation Desk & RFID Operations</h1>
        <p className="text-sm text-slate-400">Automated borrowing, check-in reconciliation, renewal, and policy enforcement</p>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 space-x-1">
        {[
          { id: 'checkout', label: 'Issue / Checkout', icon: ArrowLeftRight },
          { id: 'checkin', label: 'Check-In / Return', icon: CheckCircle2 },
          { id: 'renew', label: 'Loan Renewal', icon: RotateCw },
          { id: 'active', label: 'Active Loans', icon: Clock },
          { id: 'fines', label: 'Overdue Fines', icon: DollarSign },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center space-x-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-400 bg-slate-900/40'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab: Checkout (AC 03 & AC 04) */}
      {activeTab === 'checkout' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-sm">
            <h3 className="text-base font-semibold text-white mb-1">Issue Book Copy to Member</h3>
            <p className="text-xs text-slate-400 mb-6">
              Validates borrowing limits, reference flags, and member delinquency before disarming the RFID tag.
            </p>

            {checkoutError && (
              <div className="mb-6 p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-sm flex items-start space-x-3">
                <AlertOctagon className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="block font-semibold">Policy Restriction Enforced (AC 04)</strong>
                  <span>{checkoutError}</span>
                </div>
              </div>
            )}

            {checkoutResult && (
              <div className="mb-6 p-4 rounded-xl bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-sm flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="block font-semibold text-white">Checkout Successfully Recorded!</strong>
                  <p className="text-xs text-emerald-200 mt-1">
                    Book copy <span className="font-mono font-bold text-white">{checkoutResult.accession_number}</span> is now marked ISSUED to member{' '}
                    <strong className="text-white">{checkoutResult.member_name}</strong>. RFID Security Bit disarmed for safe exit.
                  </p>
                  <p className="text-xs text-slate-400 mt-1">Due Date: {new Date(checkoutResult.due_date).toLocaleDateString()}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleCheckout} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Member Code or Smart Card UID
                </label>
                <div className="relative">
                  <CreditCard className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                  <input
                    type="text"
                    required
                    value={checkoutMember}
                    onChange={(e) => setCheckoutMember(e.target.value)}
                    placeholder="e.g. MEM-2026-001 or CARD-MEM-STU-001"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-100 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Book Accession Number or RFID EPC
                </label>
                <div className="relative">
                  <Radio className="w-4 h-4 text-cyan-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    required
                    value={checkoutItem}
                    onChange={(e) => setCheckoutItem(e.target.value)}
                    placeholder="e.g. ACC-0884-01 or E20034120123456789010001"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-100 font-mono"
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 px-4 rounded-lg text-sm transition shadow-lg shadow-blue-600/20 disabled:opacity-50"
                >
                  {loading ? 'Validating & Issuing...' : 'Complete Checkout (Issue Book)'}
                </button>
              </div>
            </form>
          </div>

          {/* Quick Test Scenarios Guide */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>AISYS Technical Evaluation Presets</span>
            </h4>
            <p className="text-xs text-slate-400">
              One-click preset tests demonstrating strict adherence to SOP page 5 validation rules:
            </p>

            <div className="space-y-2">
              <button
                type="button"
                onClick={() => {
                  setCheckoutMember('MEM-2026-001');
                  setCheckoutItem('ACC-0884-01');
                }}
                className="w-full text-left p-3 rounded-lg bg-slate-900 hover:bg-slate-800/80 border border-slate-800 transition"
              >
                <div className="text-xs font-semibold text-emerald-400">Test Valid Standard Issue</div>
                <div className="text-[11px] text-slate-400">Aarav Sharma + Clean Code (Passes)</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setCheckoutMember('MEM-2026-001');
                  setCheckoutItem('ACC-4532-01');
                }}
                className="w-full text-left p-3 rounded-lg bg-slate-900 hover:bg-slate-800/80 border border-slate-800 transition"
              >
                <div className="text-xs font-semibold text-amber-400">Test AC 04: Reference Book Restriction</div>
                <div className="text-[11px] text-slate-400">Oxford Encyclopedia (Must Reject)</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setCheckoutMember('MEM-2026-003');
                  setCheckoutItem('ACC-0884-02');
                }}
                className="w-full text-left p-3 rounded-lg bg-slate-900 hover:bg-slate-800/80 border border-slate-800 transition"
              >
                <div className="text-xs font-semibold text-rose-400">Test AC 04: Blocked Member Restriction</div>
                <div className="text-[11px] text-slate-400">Rohan Verma (Blocked) (Must Reject)</div>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Checkin */}
      {activeTab === 'checkin' && (
        <div className="max-w-xl mx-auto bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-base font-semibold text-white mb-1">Check-In / Return Book</h3>
          <p className="text-xs text-slate-400 mb-6">
            Accepts returned copy, re-arms RFID security bit, calculates overdue fines, and marks item available.
          </p>

          {checkinError && (
            <div className="mb-6 p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-sm">
              {checkinError}
            </div>
          )}

          {checkinResult && (
            <div className="mb-6 p-4 rounded-xl bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-sm">
              <strong className="block font-semibold text-white">Return Successfully Processed!</strong>
              <p className="text-xs text-emerald-200 mt-1">
                Book copy <span className="font-mono font-bold text-white">{checkinResult.accession_number}</span> returned by{' '}
                <strong className="text-white">{checkinResult.member_name}</strong>. RFID Tag re-armed.
              </p>
            </div>
          )}

          <form onSubmit={handleCheckin} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Scan Tag EPC or Enter Accession Number
              </label>
              <div className="relative">
                <Radio className="w-4 h-4 text-cyan-400 absolute left-3 top-3" />
                <input
                  type="text"
                  required
                  value={checkinItem}
                  onChange={(e) => setCheckinItem(e.target.value)}
                  placeholder="e.g. ACC-0884-01 or E20034120123456789010001"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-100 font-mono"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2.5 px-4 rounded-lg text-sm transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              {loading ? 'Processing Check-in...' : 'Process Return & Re-arm Tag'}
            </button>
          </form>
        </div>
      )}

      {/* Tab: Renew */}
      {activeTab === 'renew' && (
        <div className="max-w-xl mx-auto bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-base font-semibold text-white mb-1">Extend Loan Period (Renew)</h3>
          <p className="text-xs text-slate-400 mb-6">
            Extends the due date by 14 days if the renewal limit (max 2 renewals) has not been exceeded.
          </p>

          {renewError && (
            <div className="mb-6 p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-sm">
              {renewError}
            </div>
          )}

          {renewResult && (
            <div className="mb-6 p-4 rounded-xl bg-blue-950/40 border border-blue-800 text-blue-300 text-sm">
              <strong className="block font-semibold text-white">Loan Successfully Renewed!</strong>
              <p className="text-xs text-blue-200 mt-1">
                New due date: <strong className="text-white">{new Date(renewResult.due_date).toLocaleDateString()}</strong> (Renewal #{renewResult.renewal_count})
              </p>
            </div>
          )}

          <form onSubmit={handleRenew} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Accession Number or RFID EPC
              </label>
              <div className="relative">
                <Radio className="w-4 h-4 text-cyan-400 absolute left-3 top-3" />
                <input
                  type="text"
                  required
                  value={renewItem}
                  onChange={(e) => setRenewItem(e.target.value)}
                  placeholder="e.g. ACC-0884-01 or E20034120123456789010001"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-100 font-mono"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 px-4 rounded-lg text-sm transition shadow-lg shadow-blue-600/20 disabled:opacity-50"
            >
              {loading ? 'Extending Loan...' : 'Renew Book Loan'}
            </button>
          </form>
        </div>
      )}

      {/* Tab: Active Loans */}
      {activeTab === 'active' && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-white">Currently Checked-Out Volumes ({activeLoans.length})</h3>
            <button onClick={loadActiveLoans} className="text-xs text-blue-400 hover:text-blue-300">
              Refresh
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/60 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Accession #</th>
                  <th className="px-4 py-3">Book Title</th>
                  <th className="px-4 py-3">Borrower</th>
                  <th className="px-4 py-3">Issued Date</th>
                  <th className="px-4 py-3">Due Date</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {activeLoans.length > 0 ? (
                  activeLoans.map((loan) => (
                    <tr key={loan.id} className="hover:bg-slate-900/40 transition">
                      <td className="px-4 py-3 font-mono text-xs font-bold text-white">{loan.accession_number}</td>
                      <td className="px-4 py-3 font-medium text-white">{loan.book_title}</td>
                      <td className="px-4 py-3">
                        <div>{loan.member_name}</div>
                        <div className="text-[11px] text-slate-400 font-mono">{loan.member_code}</div>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-400 font-mono">
                        {new Date(loan.checkout_date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-xs font-mono">
                        <span className={loan.is_overdue ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                          {new Date(loan.due_date).toLocaleDateString()}
                          {loan.is_overdue && ' (OVERDUE)'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={async () => {
                            await apiService.checkin({ accession_number: loan.accession_number });
                            loadActiveLoans();
                          }}
                          className="px-2.5 py-1 text-xs bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 rounded-md transition"
                        >
                          Return Copy
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-xs text-slate-500">
                      No active loans currently recorded.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab: Fines */}
      {activeTab === 'fines' && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-white">Overdue Penalties Ledger</h3>
            <button onClick={loadFines} className="text-xs text-blue-400 hover:text-blue-300">
              Refresh
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/60 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Member</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Reason</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {fines.length > 0 ? (
                  fines.map((f) => (
                    <tr key={f.id} className="hover:bg-slate-900/40 transition">
                      <td className="px-4 py-3">
                        <div className="font-semibold text-white">{f.member_name}</div>
                        <div className="text-[11px] text-slate-400 font-mono">{f.member_code}</div>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs font-bold text-rose-400">${f.amount.toFixed(2)}</td>
                      <td className="px-4 py-3 text-xs text-slate-400">{f.reason}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                            f.status === 'UNPAID'
                              ? 'bg-rose-950 text-rose-400 border border-rose-800'
                              : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          }`}
                        >
                          {f.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {f.status === 'UNPAID' && (
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleSettleFine(f.id, 'PAY')}
                              className="px-2.5 py-1 text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 rounded-md hover:bg-emerald-900 transition"
                            >
                              Collect Payment
                            </button>
                            <button
                              onClick={() => handleSettleFine(f.id, 'WAIVE')}
                              className="px-2.5 py-1 text-xs bg-slate-800 text-slate-300 border border-slate-700 rounded-md hover:bg-slate-700 transition"
                            >
                              Waive
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-xs text-slate-500">
                      No overdue fines on record.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
