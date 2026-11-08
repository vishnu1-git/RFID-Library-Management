export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  smart_card_uid?: string;
  roles: string[];
  created_at: string;
}

export interface BookItem {
  id: number;
  book_id: number;
  accession_number: string;
  barcode?: string;
  shelf_location?: string;
  status: 'AVAILABLE' | 'ISSUED' | 'LOST' | 'MAINTENANCE';
  created_at: string;
  epc?: string;
}

export interface Book {
  id: number;
  isbn: string;
  title: string;
  author: string;
  publisher?: string;
  publication_year?: number;
  category?: string;
  description?: string;
  is_reference_only: boolean;
  total_copies: number;
  available_copies: number;
  created_at: string;
  items?: BookItem[];
}

export interface Member {
  id: number;
  member_code: string;
  full_name: string;
  email: string;
  phone?: string;
  department?: string;
  status: 'ACTIVE' | 'BLOCKED' | 'EXPIRED';
  max_borrow_limit: number;
  outstanding_fines: number;
  card_rfid_uid?: string;
  created_at: string;
  updated_at: string;
}

export interface RFIDTag {
  id: number;
  epc: string;
  tid?: string;
  book_item_id?: number;
  is_active: boolean;
  security_bit: boolean;
  last_seen_at?: string;
  last_seen_reader?: string;
  book_title?: string;
  accession_number?: string;
}

export interface Circulation {
  id: number;
  book_item_id: number;
  book_title: string;
  accession_number: string;
  member_id: number;
  member_name: string;
  member_code: string;
  issued_by_username?: string;
  checkout_date: string;
  due_date: string;
  return_date?: string;
  renewal_count: number;
  status: 'ISSUED' | 'RETURNED' | 'OVERDUE';
  is_overdue: boolean;
  accrued_fine: number;
}

export interface Fine {
  id: number;
  circulation_id?: number;
  member_id: number;
  member_name: string;
  member_code: string;
  amount: number;
  reason: string;
  status: 'UNPAID' | 'PAID' | 'WAIVED';
  paid_at?: string;
  created_at: string;
}

export interface GateEvent {
  id: number;
  reader_id: string;
  epc: string;
  book_title?: string;
  accession_number?: string;
  is_authorized: boolean;
  alarm_triggered: boolean;
  cctv_snapshot_url?: string;
  timestamp: string;
  resolved: boolean;
  notes?: string;
}

export interface InventorySession {
  id: number;
  session_name: string;
  target_shelf?: string;
  status: 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  total_scanned: number;
  missing_count: number;
  misplaced_count: number;
  start_time: string;
  end_time?: string;
}

export interface InventoryRead {
  id: number;
  epc: string;
  book_title?: string;
  accession_number?: string;
  detected_shelf: string;
  expected_shelf?: string;
  is_misplaced: boolean;
  read_time: string;
}

export interface MigrationJob {
  id: number;
  filename: string;
  file_type: 'BOOKS' | 'MEMBERS';
  total_rows: number;
  processed_rows: number;
  error_rows: number;
  status: 'UPLOADED' | 'VALIDATING' | 'VALIDATED' | 'EXECUTED' | 'ROLLED_BACK' | 'FAILED';
  started_at: string;
  completed_at?: string;
}

export interface DashboardStats {
  total_books: number;
  available_books: number;
  issued_books: number;
  registered_members: number;
  rfid_tagged_items: number;
  active_fines_count: number;
  total_unpaid_fines: number;
  today_transactions_count: number;
  unresolved_gate_alerts_count: number;
  recent_transactions: Array<{
    id: number;
    book_title: string;
    member_name: string;
    date: string;
    status: string;
  }>;
  category_distribution: Array<{ name: string; value: number }>;
  daily_circulation_trend: Array<{ day: string; checkouts: number }>;
}

