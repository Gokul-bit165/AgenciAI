import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AgentWorkflow from './components/AgentWorkflow';
import ProviderTable from './components/ProviderTable';
import ChatInterface from './components/ChatInterface';
import { UploadCloud, CheckCircle, BarChart3, Activity, FileText } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

function App() {
    const [file, setFile] = useState(null);
    const [taskId, setTaskId] = useState(null);
    const [stage, setStage] = useState(0); // 0-5
    const [stats, setStats] = useState({ processed: 0, valid: 0 });
    const [report, setReport] = useState(null);
    const [resultData, setResultData] = useState([]);
    const [logs, setLogs] = useState([]);

    const handleUpload = async () => {
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post(`${API_URL}/upload`, formData);
            setTaskId(res.data.task_id);
            setStage(1); // Start visualization
            addLog("System", "Upload successful. Orchestrator received task.");
        } catch (e) {
            alert("Upload failed: " + e.message);
        }
    };

    const addLog = (agent, msg) => {
        setLogs(prev => [{ time: new Date().toLocaleTimeString(), agent, msg }, ...prev]);
    };

    useEffect(() => {
        if (!taskId) return;

        const interval = setInterval(async () => {
            try {
                const res = await axios.get(`${API_URL}/task/${taskId}`);
                const status = res.data.status;
                const result = res.data.result;

                if (status === 'STARTED' || status === 'PROGRESS') {
                    // Mapping 'step' metadata to visualization stages
                    if (!result) return;
                    const step = result.step || '';

                    if (step.includes('Map')) setStage(1);
                    if (step.includes('Validating')) setStage(2);

                    if (result.details) {
                        addLog("Validation Agent", `Processing ${result.details.first_name || 'record'}...`);
                    }
                } else if (status === 'SUCCESS') {
                    setStage(5);
                    setResultData(result.data);
                    setReport(result.report);
                    setStats({ processed: result.processed, valid: result.data.filter(r => r.validation_status === 'Valid').length });
                    clearInterval(interval);
                    addLog("Orchestrator", "Pipeline finished successfully.");
                }
            } catch (e) {
                console.error(e);
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [taskId]);

    return (
        <div className="min-h-screen bg-background p-8 font-sans text-white">
            <header className="max-w-7xl mx-auto mb-12 flex justify-between items-center">
                <div>
                    <h1 className="text-4xl font-black tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                        AgenciAI
                    </h1>
                    <p className="text-slate-400 mt-2">Autonomous Provider Data Validation System</p>
                </div>
                <div className="flex gap-4">
                    <div className="bg-slate-900/50 px-4 py-2 rounded-lg border border-slate-800 flex items-center gap-2">
                        <Activity size={16} className="text-green-500" />
                        <span className="text-sm font-mono text-slate-300">GPU: Active (Llama-3)</span>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Input */}
                <div className="lg:col-span-2 space-y-8">

                    <div className="glass-panel rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <UploadCloud className="text-indigo-400" /> Data Ingestion
                        </h2>

                        <div className="border-2 border-dashed border-slate-700 rounded-xl p-12 text-center hover:border-indigo-500/50 transition-colors bg-slate-900/20">
                            <input
                                type="file"
                                accept=".csv,.pdf"
                                onChange={(e) => setFile(e.target.files[0])}
                                className="hidden"
                                id="file"
                            />
                            <label htmlFor="file" className="cursor-pointer block">
                                <UploadCloud size={64} className="mx-auto text-slate-600 mb-4" />
                                <span className="text-lg font-medium text-slate-300">
                                    {file ? file.name : "Drop CSV file here or click to browse"}
                                </span>
                                <p className="text-sm text-slate-500 mt-2">Universal Parser (CSV or PDF)</p>
                            </label>
                        </div>

                        <button
                            onClick={handleUpload}
                            disabled={!file || taskId}
                            className="mt-6 w-full py-4 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-bold text-lg shadow-lg shadow-indigo-900/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Start Autonomous Pipeline
                        </button>
                    </div>

                    <div className="glass-panel rounded-2xl p-8 min-h-[400px]">
                        <h2 className="text-2xl font-bold mb-6">Agent Orchestration</h2>
                        <AgentWorkflow stage={stage} />

                        {stage === 5 && (
                            <div className="mt-8 p-6 bg-green-900/20 border border-green-500/30 rounded-xl flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <CheckCircle size={32} className="text-green-400" />
                                    <div>
                                        <h3 className="text-xl font-bold text-green-100">Validation Complete</h3>
                                        <p className="text-green-400/80">Processed {stats.processed} records successfully.</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-3xl font-black text-white">{Math.round((stats.valid / stats.processed) * 100)}%</div>
                                    <div className="text-xs uppercase tracking-wider text-green-400">Accuracy Score</div>
                                </div>
                            </div>
                        )}
                    </div>

                    {stage === 5 && (
                        <div className="glass-panel rounded-2xl p-8">
                            <ProviderTable data={resultData} report={report} taskId={taskId} />
                        </div>
                    )}

                    {/* Chat Interface - Always visible if task started */}
                    {taskId && <ChatInterface taskId={taskId} />}

                </div>

                {/* Right Column: Logs & Stats */}
                <div className="space-y-8">
                    <div className="glass-panel rounded-2xl p-6 h-[600px] overflow-hidden flex flex-col">
                        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                            <BarChart3 size={20} className="text-cyan-400" /> Live Agent Logs
                        </h3>
                        <div className="flex-1 overflow-y-auto space-y-3 pr-2 font-mono text-xs">
                            {logs.map((log, i) => (
                                <div key={i} className="p-3 bg-black/20 rounded border-l-2 border-indigo-500">
                                    <div className="flex justify-between text-slate-500 mb-1">
                                        <span>{log.agent}</span>
                                        <span>{log.time}</span>
                                    </div>
                                    <div className="text-slate-300">{log.msg}</div>
                                </div>
                            ))}
                            {logs.length === 0 && <div className="text-center text-slate-600 mt-20">Waiting for task...</div>}
                        </div>
                    </div>
                </div>

            </main>
        </div>
    )
}

export default App
