import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Shield, CreditCard, LogOut, User as UserIcon, Activity } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, smartCardLogin } = useAuth();
  const [smartCardUid, setSmartCardUid] = useState('');
  const [showCardModal, setShowCardModal] = useState(false);

  const handleSimulatedCard = async (uid: string) => {
    try {
      await smartCardLogin(uid);
      setShowCardModal(false);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Smart card login failed');
    }
  };

  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & System Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Operational DB: <strong className="text-emerald-400">PostgreSQL</strong>
          </span>
        </div>
        <div className="h-4 w-px bg-slate-800"></div>
        <div className="flex items-center space-x-1.5 text-xs text-blue-400 bg-blue-950/60 px-2.5 py-1 rounded-full border border-blue-800/50">
          <Activity className="w-3.5 h-3.5" />
          <span>RFID Middleware: Ready</span>
        </div>
      </div>

      {/* User Controls & Smart Card Login */}
      <div className="flex items-center space-x-3">
        {/* Simulate Smart Card Tap (AC 07) */}
        <button
          onClick={() => setShowCardModal(true)}
          className="flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition"
          title="Simulate Staff Smart Card Tap"
        >
          <CreditCard className="w-3.5 h-3.5 text-indigo-400" />
          <span>Tap Smart Card</span>
        </button>

        {user ? (
          <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
            <div className="text-right">
              <p className="text-sm font-medium text-slate-200 leading-none">{user.full_name}</p>
              <p className="text-xs text-slate-400 mt-1 capitalize">{user.roles.join(', ') || 'Staff'}</p>
            </div>
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-semibold text-xs border border-indigo-400/30">
              {user.username.slice(0, 2).toUpperCase()}
            </div>
            <button
              onClick={logout}
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 rounded-lg transition"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="text-xs text-slate-400">Not Logged In</div>
        )}
      </div>

      {/* Simulated Smart Card Dialog */}
      {showCardModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center space-x-3 text-indigo-400 mb-4">
              <CreditCard className="w-6 h-6" />
              <h3 className="text-lg font-semibold text-white">Staff Smart Card Reader (AC 07)</h3>
            </div>
            <p className="text-sm text-slate-400 mb-4">
              Simulate tapping an authorized staff smart card on the contactless desk reader to log in instantly via RBAC.
            </p>
            <div className="space-y-2 mb-6">
              <button
                onClick={() => handleSimulatedCard('CARD-STAFF-ADMIN-01')}
                className="w-full text-left p-3 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 flex justify-between items-center transition"
              >
                <div>
                  <div className="text-sm font-medium text-white">System Administrator Card</div>
                  <div className="text-xs text-slate-400 font-mono">UID: CARD-STAFF-ADMIN-01</div>
                </div>
                <span className="text-xs bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded border border-indigo-800">Admin</span>
              </button>

              <button
                onClick={() => handleSimulatedCard('CARD-STAFF-LIB-02')}
                className="w-full text-left p-3 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 flex justify-between items-center transition"
              >
                <div>
                  <div className="text-sm font-medium text-white">Chief Librarian Card</div>
                  <div className="text-xs text-slate-400 font-mono">UID: CARD-STAFF-LIB-02</div>
                </div>
                <span className="text-xs bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">Librarian</span>
              </button>
            </div>
            <div className="flex justify-end">
              <button
                onClick={() => setShowCardModal(false)}
                className="px-4 py-2 text-sm text-slate-400 hover:text-white"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

