import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Search, FileText, Database, CheckCircle, Loader2 } from 'lucide-react';

const AgentCard = ({ title, icon: Icon, status, delay }) => {
    const isActive = status === 'processing';
    const isDone = status === 'completed';

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            className={`agent-card flex flex-col items-center text-center ${isActive ? 'ring-2 ring-indigo-500 border-indigo-500 bg-indigo-950/20' : ''}`}
        >
            <div className={`p-4 rounded-full mb-4 ${isActive ? 'bg-indigo-600 animate-pulse' : isDone ? 'bg-green-600' : 'bg-slate-800'}`}>
                <Icon size={32} className="text-white" />
            </div>
            <h3 className="text-lg font-bold mb-2">{title}</h3>
            <div className="text-xs text-slate-400 h-6">
                {isActive && <span className="text-indigo-400 flex items-center justify-center gap-1"><Loader2 size={12} className="animate-spin" /> Working...</span>}
                {isDone && <span className="text-green-400 flex items-center justify-center gap-1"><CheckCircle size={12} /> Complete</span>}
                {!isActive && !isDone && "Waiting..."}
            </div>
        </motion.div>
    );
};

const AgentWorkflow = ({ stage }) => {
    // stage: 0=idle, 1=validating, 2=enriching, 3=qa, 4=updating, 5=done
    return (
        <div className="w-full grid grid-cols-1 md:grid-cols-4 gap-4 my-8">
            <AgentCard
                title="Validation Agent"
                icon={ShieldCheck}
                delay={0.1}
                status={stage === 1 ? 'processing' : stage > 1 ? 'completed' : 'idle'}
            />
            <AgentCard
                title="Enrichment Agent"
                icon={Search}
                delay={0.2}
                status={stage === 2 ? 'processing' : stage > 2 ? 'completed' : 'idle'}
            />
            <AgentCard
                title="QA Agent"
                icon={FileText}
                delay={0.3}
                status={stage === 3 ? 'processing' : stage > 3 ? 'completed' : 'idle'}
            />
            <AgentCard
                title="Directory Agent"
                icon={Database}
                delay={0.4}
                status={stage === 4 ? 'processing' : stage > 4 ? 'completed' : 'idle'}
            />
        </div>
    );
};

export default AgentWorkflow;
