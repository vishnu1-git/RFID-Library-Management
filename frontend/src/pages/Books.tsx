import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { Book } from '../types';
import {
  BookOpen,
  Search,
  Plus,
  Radio,
  Bookmark,
  CheckCircle2,
  XCircle,
  Layers,
  ChevronDown,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const Books: React.FC = () => {
  const { hasRole } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [expandedBookId, setExpandedBookId] = useState<number | null>(null);
  const [bookDetails, setBookDetails] = useState<Record<number, Book>>({});
  const [showAddModal, setShowAddModal] = useState(false);

  // Form state
  const [isbn, setIsbn] = useState('');
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [publisher, setPublisher] = useState('');
  const [category, setCategory] = useState('Computer Science');
  const [isReference, setIsReference] = useState(false);
  const [copies, setCopies] = useState(2);
  const [submitting, setSubmitting] = useState(false);

  const fetchBooks = async (query?: string) => {
    setLoading(true);
    try {
      const data = await apiService.getBooks(query);
      setBooks(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks(search);
  }, [search]);

  const toggleExpand = async (bookId: number) => {
    if (expandedBookId === bookId) {
      setExpandedBookId(null);
      return;
    }
    setExpandedBookId(bookId);
    if (!bookDetails[bookId]) {
      try {
        const fullBook = await apiService.getBookById(bookId);
        setBookDetails((prev) => ({ ...prev, [bookId]: fullBook }));
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleCreateBook = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiService.createBook({
        isbn,
        title,
        author,
        publisher,
        category,
        is_reference_only: isReference,
        total_copies: Number(copies),
      });
      setShowAddModal(false);
      // Reset form
      setIsbn('');
      setTitle('');
      setAuthor('');
      setPublisher('');
      setIsReference(false);
      setCopies(2);
      fetchBooks();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create book');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Bibliographic Catalogue</h1>
          <p className="text-sm text-slate-400">Manage titles, reference restrictions, and physical copy inventory</p>
        </div>

        {hasRole('Librarian') && (
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow-md shadow-blue-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>Add New Title</span>
          </button>
        )}
      </div>

      {/* Search and Filters */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex items-center space-x-3">
        <Search className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by title, author, category, or ISBN..."
          className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
        />
        {search && (
          <button onClick={() => setSearch('')} className="text-xs text-slate-400 hover:text-white px-2">
            Clear
          </button>
        )}
      </div>

      {/* Book List Table */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/70 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3.5 w-10"></th>
                <th className="px-4 py-3.5">Title & Author</th>
                <th className="px-4 py-3.5">ISBN</th>
                <th className="px-4 py-3.5">Category</th>
                <th className="px-4 py-3.5">Borrowing Restriction</th>
                <th className="px-4 py-3.5">Availability</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {books.length > 0 ? (
                books.map((b) => {
                  const isExpanded = expandedBookId === b.id;
                  const details = bookDetails[b.id];
                  return (
                    <React.Fragment key={b.id}>
                      <tr
                        onClick={() => toggleExpand(b.id)}
                        className="hover:bg-slate-900/50 cursor-pointer transition"
                      >
                        <td className="px-4 py-3.5 text-slate-500">
                          {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        </td>
                        <td className="px-4 py-3.5">
                          <div className="font-semibold text-white">{b.title}</div>
                          <div className="text-xs text-slate-400">{b.author}</div>
                        </td>
                        <td className="px-4 py-3.5 font-mono text-xs text-slate-300">{b.isbn}</td>
                        <td className="px-4 py-3.5">
                          <span className="px-2.5 py-0.5 rounded-full text-xs bg-slate-800 text-slate-300 border border-slate-700">
                            {b.category || 'General'}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">
                          {b.is_reference_only ? (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-950/70 text-amber-400 border border-amber-800">
                              <Bookmark className="w-3 h-3" />
                              <span>Reference Only (No Issue)</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-950/50 text-blue-400 border border-blue-800/50">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Standard Loan</span>
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3.5">
                          <div className="flex items-center space-x-2">
                            <span className="font-semibold text-white">{b.available_copies}</span>
                            <span className="text-xs text-slate-400">/ {b.total_copies} available</span>
                          </div>
                        </td>
                      </tr>

                      {/* Physical Copies Detail Row */}
                      {isExpanded && (
                        <tr className="bg-slate-900/70">
                          <td colSpan={6} className="px-8 py-4">
                            <div className="border border-slate-800 rounded-lg p-4 bg-slate-950/60">
                              <div className="flex justify-between items-center mb-3">
                                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
                                  <Layers className="w-3.5 h-3.5 text-blue-400" />
                                  <span>Physical Inventory Copies & Associated RFID Tags</span>
                                </h4>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                {(details?.items ?? []).map((item) => (
                                  <div
                                    key={item.id}
                                    className="p-3 rounded-lg border border-slate-800 bg-slate-900/90 space-y-1.5"
                                  >
                                    <div className="flex justify-between items-center">
                                      <span className="font-mono text-xs font-bold text-white">{item.accession_number}</span>
                                      <span
                                        className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                                          item.status === 'AVAILABLE'
                                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                            : 'bg-amber-950 text-amber-400 border border-amber-800'
                                        }`}
                                      >
                                        {item.status}
                                      </span>
                                    </div>
                                    <div className="text-[11px] text-slate-400">
                                      Location: <span className="font-mono text-slate-300">{item.shelf_location || 'Unassigned'}</span>
                                    </div>
                                    <div className="text-[11px] text-slate-400 flex items-center space-x-1.5">
                                      <Radio className="w-3 h-3 text-cyan-400" />
                                      {item.epc ? (
                                        <span className="font-mono text-[10px] text-cyan-300 truncate" title={item.epc}>
                                          EPC: {item.epc}
                                        </span>
                                      ) : (
                                        <span className="text-[10px] text-slate-500 italic">No RFID Tag Encoded</span>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-xs text-slate-500">
                    {loading ? 'Searching catalogue...' : 'No books matching your query found.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Book Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4">Add New Bibliographic Title</h3>
            <form onSubmit={handleCreateBook} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">ISBN Number</label>
                <input
                  type="text"
                  required
                  value={isbn}
                  onChange={(e) => setIsbn(e.target.value)}
                  placeholder="e.g. 978-0131103627"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Book Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Clean Architecture"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Author(s)</label>
                  <input
                    type="text"
                    required
                    value={author}
                    onChange={(e) => setAuthor(e.target.value)}
                    placeholder="Author name"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Category</label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder="e.g. Algorithms"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 items-center">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Number of Copies</label>
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={copies}
                    onChange={(e) => setCopies(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
                  />
                </div>
                <div className="pt-5">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isReference}
                      onChange={(e) => setIsReference(e.target.checked)}
                      className="rounded bg-slate-950 border-slate-700 text-blue-600 focus:ring-0"
                    />
                    <span className="text-xs text-slate-300 font-medium">Reference Only (AC 04)</span>
                  </label>
                </div>
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
                  {submitting ? 'Creating...' : 'Save Book & Generate Copies'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

