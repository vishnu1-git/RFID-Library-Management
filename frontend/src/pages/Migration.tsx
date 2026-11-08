import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { MigrationJob } from '../types';
import {
  FileSpreadsheet,
  Upload,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  ArrowRight,
  ShieldCheck,
  FileCheck,
  RefreshCw,
  Info
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const MigrationPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [jobs, setJobs] = useState<MigrationJob[]>([]);
  const [selectedJob, setSelectedJob] = useState<any | null>(null);
  const [fileType, setFileType] = useState<'BOOKS' | 'MEMBERS'>('BOOKS');
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);

  const fetchJobs = async () => {
    try {
      const data = await apiService.getMigrationJobs();
      setJobs(data);
      if (data.length > 0 && !selectedJob) {
        loadJobDetail(data[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadJobDetail = async (jobId: number) => {
    try {
      const detail = await apiService.getMigrationJobDetail(jobId);
      setSelectedJob(detail);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploading(true);
    try {
      const job = await apiService.uploadMigrationFile(file, fileType);
      await fetchJobs();
      await loadJobDetail(job.id);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to upload spreadsheet');
    } finally {
      setUploading(false);
    }
  };

  const handleValidate = async () => {
    if (!selectedJob) return;
    setProcessing(true);
    try {
      await apiService.validateMigration(selectedJob.id);
      await loadJobDetail(selectedJob.id);
      await fetchJobs();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Validation failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleExecute = async () => {
    if (!selectedJob) return;
    setProcessing(true);
    try {
      await apiService.executeMigration(selectedJob.id);
      await loadJobDetail(selectedJob.id);
      await fetchJobs();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Execution failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleRollback = async () => {
    if (!selectedJob) return;
    if (!confirm('Are you sure you want to rollback all records committed by this migration job?')) return;
    setProcessing(true);
    try {
      await apiService.rollbackMigration(selectedJob.id);
      await loadJobDetail(selectedJob.id);
      await fetchJobs();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Rollback failed');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Controlled Data Migration (AC 01 & AC 10)</h1>
          <p className="text-sm text-slate-400">
            Staging-first pipeline with duplicate detection, schema validation, and atomic rollback
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs bg-emerald-950/80 text-emerald-300 border border-emerald-800/80 px-3 py-1.5 rounded-lg flex items-center space-x-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>ILMS Protection: Active</span>
          </span>
        </div>
      </div>

      {/* Safety Policy Alert */}
      <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-start space-x-3 text-xs text-slate-300">
        <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-white block font-semibold mb-0.5">Core Engineering Principle (AISYS SOP Pages 1 & 3):</strong>
          Spreadsheet records are staged into an isolated staging buffer (<code className="text-blue-300">migration_staging</code>). Validation checks against existing operational records for duplicate ISBNs or member codes before approval. Existing external ILMS records are never overwritten.
        </div>
      </div>

      {/* Upload Box */}
      {hasRole('Admin') && (
        <div className="bg-slate-950 border-2 border-dashed border-slate-800 hover:border-slate-700 rounded-xl p-6 transition flex flex-col items-center justify-center text-center">
          <FileSpreadsheet className="w-10 h-10 text-blue-400 mb-2" />
          <h3 className="text-sm font-semibold text-white">Upload Legacy Excel or CSV Data File</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-md">
            Compatible with sample files in <code className="text-slate-300 font-mono">sample-data/books.xlsx</code> and <code className="text-slate-300 font-mono">sample-data/members.xlsx</code>.
          </p>

          <div className="flex items-center space-x-4 mt-4">
            <div className="flex items-center space-x-2 text-xs">
              <label className="text-slate-400">Dataset Type:</label>
              <select
                value={fileType}
                onChange={(e) => setFileType(e.target.value as any)}
                className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-200"
              >
                <option value="BOOKS">Bibliographic Books Catalog</option>
                <option value="MEMBERS">Student / Faculty Members</option>
              </select>
            </div>

            <label className="cursor-pointer bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center space-x-1.5 shadow-md shadow-blue-600/20">
              <Upload className="w-3.5 h-3.5" />
              <span>{uploading ? 'Staging Data...' : 'Choose Spreadsheet File'}</span>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
          </div>
        </div>
      )}

      {/* Selected Job Staging Pipeline Panel */}
      {selectedJob && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
          <div className="flex flex-col md:flex-row justify-between md:items-center pb-4 border-b border-slate-850 gap-4">
            <div>
              <span className="text-xs font-mono text-slate-400">JOB #{selectedJob.id}</span>
              <h2 className="text-lg font-bold text-white mt-0.5">{selectedJob.filename}</h2>
              <p className="text-xs text-slate-400 font-mono">Type: {selectedJob.file_type} | Staged Rows: {selectedJob.total_rows}</p>
            </div>

            {/* Pipeline Stage Buttons */}
            <div className="flex items-center space-x-2">
              {selectedJob.status === 'UPLOADED' && (
                <button
                  onClick={handleValidate}
                  disabled={processing}
                  className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-xs font-semibold transition"
                >
                  <FileCheck className="w-3.5 h-3.5" />
                  <span>Run Validation & Duplicate Check (AC 01)</span>
                </button>
              )}

              {selectedJob.status === 'VALIDATED' && (
                <button
                  onClick={handleExecute}
                  disabled={processing}
                  className="flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-xs font-semibold transition shadow-md shadow-emerald-600/20"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Migrate Approved Records to Operational DB</span>
                </button>
              )}

              {selectedJob.status === 'EXECUTED' && (
                <button
                  onClick={handleRollback}
                  disabled={processing}
                  className="flex items-center space-x-1.5 bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-lg text-xs font-semibold transition shadow-md shadow-rose-600/20"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Rollback Migration (AC 10 Recovery)</span>
                </button>
              )}
            </div>
          </div>

          {/* Pipeline Stage Progression Pill */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400 font-medium">Pipeline Status:</span>
            <span
              className={`px-3 py-1 rounded-full font-mono font-bold ${
                selectedJob.status === 'EXECUTED'
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : selectedJob.status === 'ROLLED_BACK'
                  ? 'bg-amber-950 text-amber-400 border border-amber-800'
                  : selectedJob.status === 'VALIDATED'
                  ? 'bg-blue-950 text-blue-400 border border-blue-800'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              {selectedJob.status}
            </span>
            <span className="text-slate-500 ml-4 font-mono">
              Committed: {selectedJob.processed_rows} / Errors: {selectedJob.error_rows}
            </span>
          </div>

          {/* Validation Errors Table (if any) */}
          {(selectedJob.errors ?? []).length > 0 && (
            <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-900/60">
              <h4 className="text-xs font-bold text-rose-300 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Validation & Duplicate Collision Errors Detected ({selectedJob.errors.length})</span>
              </h4>
              <p className="text-xs text-rose-200/80 mb-3">
                Invalid records are automatically isolated and rejected to preserve relational database integrity.
              </p>
              <div className="overflow-x-auto border border-rose-900/50 rounded-lg">
                <table className="w-full text-left text-xs text-rose-200">
                  <thead className="bg-rose-950/80 uppercase text-[10px] tracking-wider text-rose-300">
                    <tr>
                      <th className="px-3 py-2">Row #</th>
                      <th className="px-3 py-2">Target Field</th>
                      <th className="px-3 py-2">Validation Failure Reason</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-rose-950">
                    {selectedJob.errors.map((err: any) => (
                      <tr key={err.id}>
                        <td className="px-3 py-2 font-mono font-bold">{err.row_number}</td>
                        <td className="px-3 py-2 font-mono text-rose-300">{err.field_name || 'row'}</td>
                        <td className="px-3 py-2 font-medium">{err.error_reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Staged Data Preview */}
          <div>
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
              Sample Staged Records (<code className="text-cyan-400">migration_staging</code>)
            </h4>
            <div className="overflow-x-auto border border-slate-800 rounded-lg">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900 uppercase text-[10px] tracking-wider text-slate-400">
                  <tr>
                    <th className="px-3 py-2.5">Staging Status</th>
                    <th className="px-3 py-2.5">Key Field</th>
                    <th className="px-3 py-2.5">Primary Descriptor</th>
                    <th className="px-3 py-2.5">Secondary Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  {(selectedJob.sample_staging ?? []).map((row: any, i: number) => (
                    <tr key={i} className="hover:bg-slate-900/40">
                      <td className="px-3 py-2 font-mono">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            row._status === 'VALID'
                              ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                              : row._status === 'COMMITTED'
                              ? 'bg-blue-950 text-blue-400 border border-blue-800'
                              : row._status === 'INVALID'
                              ? 'bg-rose-950 text-rose-400 border border-rose-800'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {row._status}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-mono text-cyan-300">{row.isbn || row.member_code || row.ISBN || '-'}</td>
                      <td className="px-3 py-2 font-medium text-white">{row.title || row.full_name || row.Title || '-'}</td>
                      <td className="px-3 py-2 text-slate-400">{row.author || row.email || row.Author || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Migration Jobs History Table */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-sm font-semibold text-white">Migration Execution Journal</h3>
          <button onClick={fetchJobs} className="text-xs text-blue-400 hover:text-blue-300">
            Refresh Jobs
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/70 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Job ID</th>
                <th className="px-4 py-3">Spreadsheet File</th>
                <th className="px-4 py-3">Dataset</th>
                <th className="px-4 py-3">Total Rows</th>
                <th className="px-4 py-3">Errors</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {jobs.length > 0 ? (
                jobs.map((j) => (
                  <tr key={j.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">JOB-{j.id}</td>
                    <td className="px-4 py-3 font-medium text-white">{j.filename}</td>
                    <td className="px-4 py-3 text-xs text-slate-300">{j.file_type}</td>
                    <td className="px-4 py-3 font-mono text-xs">{j.total_rows}</td>
                    <td className="px-4 py-3 font-mono text-xs text-rose-400">{j.error_rows}</td>
                    <td className="px-4 py-3">
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {j.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => loadJobDetail(j.id)}
                        className="text-xs text-blue-400 hover:text-blue-300 underline font-medium"
                      >
                        Inspect Pipeline
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-xs text-slate-500">
                    No migration jobs uploaded yet.
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
