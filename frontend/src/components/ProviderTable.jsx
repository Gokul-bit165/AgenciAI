import React from 'react';
import { AlertCircle, CheckCircle, XCircle, ExternalLink, Globe, Download } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

const ProviderTable = ({ data, report, taskId }) => {
    if (!data || data.length === 0) return null;

    const handleDownload = () => {
        window.location.href = `${API_URL}/download/${taskId}`;
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                    Directory Validation Report
                </h2>
                <button
                    onClick={handleDownload}
                    className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-sm font-bold transition-colors"
                >
                    <Download size={16} /> Download CSV
                </button>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                    <div className="text-slate-400 text-sm">Total Processed</div>
                    <div className="text-2xl font-bold">{report?.total_processed}</div>
                </div>
                <div className="bg-green-900/20 p-4 rounded-xl border border-green-700/50">
                    <div className="text-green-400 text-sm">Valid Providers</div>
                    <div className="text-2xl font-bold text-green-300">{report?.valid_providers}</div>
                </div>
                <div className="bg-red-900/20 p-4 rounded-xl border border-red-700/50">
                    <div className="text-red-400 text-sm">Action Items</div>
                    <div className="text-2xl font-bold text-red-300">{report?.flagged_providers}</div>
                </div>
                <div className="bg-indigo-900/20 p-4 rounded-xl border border-indigo-700/50">
                    <div className="text-indigo-400 text-sm">Accuracy Rate</div>
                    <div className="text-2xl font-bold text-indigo-300">{(report?.accuracy_rate * 100).toFixed(1)}%</div>
                </div>
            </div>

            {/* Detailed Table */}
            <div className="overflow-x-auto rounded-xl border border-slate-700">
                <table className="w-full text-left text-sm text-slate-400">
                    <thead className="bg-slate-800 text-slate-200 uppercase font-medium">
                        <tr>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4">Provider</th>
                            <th className="px-6 py-4">NPI</th>
                            <th className="px-6 py-4">Confidence</th>
                            <th className="px-6 py-4">Enrichment</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700 bg-slate-900/50">
                        {data.map((row, i) => (
                            <tr key={i} className="hover:bg-slate-800/50 transition-colors">
                                <td className="px-6 py-4">
                                    <div className={`flex items-center gap-2 px-3 py-1 rounded-full w-fit text-xs font-bold
                                        ${row.validation_status === 'Valid' ? 'bg-green-900/30 text-green-400 border border-green-700' : 'bg-amber-900/30 text-amber-400 border border-amber-700'}
                                    `}>
                                        {row.validation_status === 'Valid' ? <CheckCircle size={12} /> : <AlertCircle size={12} />}
                                        {row.validation_status}
                                    </div>
                                    {row.website_validation && !row.website_validation.valid && (
                                        <div className="mt-1 flex items-center gap-1 text-red-400 text-xs">
                                            <Globe size={10} /> Website Unreachable
                                        </div>
                                    )}
                                </td>
                                <td className="px-6 py-4 font-medium text-white">
                                    {row.record.first_name} {row.record.last_name}
                                    {row.issues && row.issues.length > 0 && (
                                        <div className="mt-1 text-xs text-red-400">
                                            Issues: {row.issues.join(", ")}
                                        </div>
                                    )}
                                </td>
                                <td className="px-6 py-4 font-mono">{row.record.npi}</td>
                                <td className="px-6 py-4">
                                    <div className="w-full bg-slate-700 rounded-full h-2 w-24 overflow-hidden">
                                        <div
                                            className={`h-full ${row.confidence_score > 0.8 ? 'bg-green-500' : row.confidence_score > 0.5 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                            style={{ width: `${row.confidence_score * 100}%` }}
                                        />
                                    </div>
                                    <span className="text-xs mt-1 block">{row.confidence_score * 100}%</span>
                                </td>
                                <td className="px-6 py-4 text-xs">
                                    {row.enriched && row.enriched.specialties ? (
                                        <div className="space-y-1">
                                            {row.enriched.specialties.map(s => (
                                                <span key={s} className="inline-block bg-slate-800 px-2 py-0.5 rounded mr-1 mb-1">{s}</span>
                                            ))}
                                            {row.enriched.certification && (
                                                <div className="text-indigo-400">{row.enriched.certification}</div>
                                            )}
                                        </div>
                                    ) : (
                                        <span className="opacity-50">-</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ProviderTable;
