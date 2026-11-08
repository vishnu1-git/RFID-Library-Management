import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Books } from './pages/Books';
import { Members } from './pages/Members';
import { CirculationPage } from './pages/Circulation';
import { RFIDTagsPage } from './pages/RFIDTags';
import { InventoryPage } from './pages/Inventory';
import { GateEventsPage } from './pages/GateEvents';
import { MigrationPage } from './pages/Migration';
import { ReportsPage } from './pages/Reports';
import { AdminPage } from './pages/Admin';
import { SettingsPage } from './pages/Settings';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">
        Authenticating session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<Dashboard />} />
            <Route path="/books" element={<Books />} />
            <Route path="/members" element={<Members />} />
            <Route path="/circulation" element={<CirculationPage />} />
            <Route path="/rfid" element={<RFIDTagsPage />} />
            <Route path="/inventory" element={<InventoryPage />} />
            <Route path="/gates" element={<GateEventsPage />} />
            <Route path="/migration" element={<MigrationPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;

