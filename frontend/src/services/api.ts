import axios from 'axios';
import {
  User,
  Book,
  Member,
  Circulation,
  Fine,
  RFIDTag,
  InventorySession,
  GateEvent,
  MigrationJob,
  DashboardStats
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token or simulated SmartCard UID if stored
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('librasync_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const smartCardUid = localStorage.getItem('librasync_smartcard');
  if (smartCardUid) {
    config.headers['X-Smartcard-UID'] = smartCardUid;
  }
  return config;
});

export const apiService = {
  // System Health
  getHealth: async () => {
    const res = await axios.get('http://localhost:8000/health');
    return res.data;
  },

  // Auth
  login: async (credentials: { username: string; password: string }) => {
    const res = await api.post('/auth/login', credentials);
    return res.data;
  },
  smartCardLogin: async (smartCardUid: string) => {
    const res = await api.post('/auth/smartcard-login', { smart_card_uid: smartCardUid });
    return res.data;
  },
  getCurrentUser: async (): Promise<User> => {
    const res = await api.get('/auth/me');
    return res.data;
  },

  // Books / Catalog
  getBooks: async (query?: string): Promise<Book[]> => {
    const res = await api.get('/books', { params: { q: query } });
    return res.data;
  },
  getBookById: async (id: number): Promise<Book> => {
    const res = await api.get(`/books/${id}`);
    return res.data;
  },
  createBook: async (data: Partial<Book> & { total_copies: number }): Promise<Book> => {
    const res = await api.post('/books', data);
    return res.data;
  },
  addCopy: async (bookId: number, data: { accession_number: string; shelf_location?: string }) => {
    const res = await api.post(`/books/${bookId}/items`, data);
    return res.data;
  },

  // Members
  getMembers: async (query?: string): Promise<Member[]> => {
    const res = await api.get('/members', { params: { q: query } });
    return res.data;
  },
  createMember: async (data: Partial<Member>): Promise<Member> => {
    const res = await api.post('/members', data);
    return res.data;
  },
  updateMemberStatus: async (memberId: number, status: string): Promise<Member> => {
    const res = await api.patch(`/members/${memberId}/status`, null, { params: { status } });
    return res.data;
  },

  // Circulation
  checkout: async (data: { accession_number?: string; epc?: string; member_code: string }): Promise<Circulation> => {
    const res = await api.post('/circulation/checkout', data);
    return res.data;
  },
  checkin: async (data: { accession_number?: string; epc?: string }): Promise<Circulation> => {
    const res = await api.post('/circulation/checkin', data);
    return res.data;
  },
  renew: async (data: { circulation_id?: number; epc?: string; accession_number?: string }): Promise<Circulation> => {
    const res = await api.post('/circulation/renew', data);
    return res.data;
  },
  getActiveCirculation: async (): Promise<Circulation[]> => {
    const res = await api.get('/circulation/active');
    return res.data;
  },
  getCirculationHistory: async (): Promise<Circulation[]> => {
    const res = await api.get('/circulation/history');
    return res.data;
  },
  getFines: async (): Promise<Fine[]> => {
    const res = await api.get('/circulation/fines');
    return res.data;
  },
  settleFine: async (fineId: number, action: 'PAY' | 'WAIVE'): Promise<Fine> => {
    const res = await api.post('/circulation/fines/settle', { fine_id: fineId, action });
    return res.data;
  },

  // RFID
  scanRFID: async (event: { reader_id: string; epc: string }) => {
    const res = await api.post('/rfid/scan', event);
    return res.data;
  },
  associateRFIDTag: async (data: { epc: string; accession_number?: string; book_item_id?: number }): Promise<RFIDTag> => {
    const res = await api.post('/rfid/tag', data);
    return res.data;
  },
  getTags: async (): Promise<RFIDTag[]> => {
    const res = await api.get('/rfid/tags');
    return res.data;
  },

  // Inventory
  getInventorySessions: async (): Promise<InventorySession[]> => {
    const res = await api.get('/inventory/sessions');
    return res.data;
  },
  startInventory: async (data: { session_name: string; target_shelf?: string }): Promise<InventorySession> => {
    const res = await api.post('/inventory/start', data);
    return res.data;
  },
  scanInventoryItem: async (data: { session_id: number; epc: string; detected_shelf: string }) => {
    const res = await api.post('/inventory/scan', data);
    return res.data;
  },
  completeInventory: async (sessionId: number): Promise<InventorySession> => {
    const res = await api.post(`/inventory/${sessionId}/complete`);
    return res.data;
  },
  getInventoryResults: async (sessionId: number) => {
    const res = await api.get(`/inventory/${sessionId}/results`);
    return res.data;
  },

  // Security Gates
  getGateEvents: async (): Promise<GateEvent[]> => {
    const res = await api.get('/gates/events');
    return res.data;
  },
  triggerGateEvent: async (data: { reader_id: string; epc: string }): Promise<GateEvent> => {
    const res = await api.post('/gates/events', data);
    return res.data;
  },
  resolveGateEvent: async (eventId: number, notes?: string): Promise<GateEvent> => {
    const res = await api.post(`/gates/events/${eventId}/resolve`, { event_id: eventId, notes });
    return res.data;
  },

  // Migration
  uploadMigrationFile: async (file: File, fileType: 'BOOKS' | 'MEMBERS'): Promise<MigrationJob> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post(`/migration/upload?file_type=${fileType}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  validateMigration: async (jobId: number): Promise<MigrationJob> => {
    const res = await api.post(`/migration/validate/${jobId}`);
    return res.data;
  },
  executeMigration: async (jobId: number): Promise<MigrationJob> => {
    const res = await api.post('/migration/execute', { job_id: jobId });
    return res.data;
  },
  rollbackMigration: async (jobId: number): Promise<MigrationJob> => {
    const res = await api.post('/migration/rollback', { job_id: jobId });
    return res.data;
  },
  getMigrationJobs: async (): Promise<MigrationJob[]> => {
    const res = await api.get('/migration/jobs');
    return res.data;
  },
  getMigrationJobDetail: async (jobId: number) => {
    const res = await api.get(`/migration/jobs/${jobId}`);
    return res.data;
  },

  // Reports & Dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await api.get('/reports/dashboard');
    return res.data;
  },

  // Admin & Audit
  getAuditLogs: async (action?: string) => {
    const res = await api.get('/admin/audit-logs', { params: { action } });
    return res.data;
  },
  getUsers: async (): Promise<User[]> => {
    const res = await api.get('/admin/users');
    return res.data;
  },
};

export default api;
