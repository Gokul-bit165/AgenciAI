import React, { useState } from 'react';
import axios from 'axios';
import { MessageSquare, Send, X } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

const ChatInterface = ({ taskId }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Hello! I am your Data Assistant. Ask me anything about the validation results.' }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim() || !taskId) return;

        const userMsg = input;
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setInput("");
        setLoading(true);

        try {
            const res = await axios.post(`${API_URL}/chat`, {
                task_id: taskId,
                message: userMsg
            });
            setMessages(prev => [...prev, { role: 'assistant', text: res.data.response }]);
        } catch (e) {
            setMessages(prev => [...prev, { role: 'assistant', text: "Sorry, I encountered an error." }]);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-8 right-8 bg-indigo-600 p-4 rounded-full shadow-lg hover:bg-indigo-500 transition-all z-50 pointer-events-auto"
            >
                <MessageSquare size={24} className="text-white" />
            </button>
        );
    }

    return (
        <div className="fixed bottom-8 right-8 w-96 h-[500px] bg-slate-900 border border-slate-700 rounded-xl shadow-2xl flex flex-col z-50 pointer-events-auto overflow-hidden font-sans">
            <div className="p-4 bg-slate-800 border-b border-slate-700 flex justify-between items-center">
                <h3 className="font-bold text-white flex items-center gap-2">
                    <MessageSquare size={16} className="text-indigo-400" /> Data Assistant
                </h3>
                <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white">
                    <X size={18} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-lg text-sm ${m.role === 'user'
                                ? 'bg-indigo-600 text-white rounded-br-none'
                                : 'bg-slate-700 text-slate-200 rounded-bl-none'
                            }`}>
                            {m.text}
                        </div>
                    </div>
                ))}
                {loading && <div className="text-slate-500 text-xs italic ml-2">Thinking...</div>}
            </div>

            <div className="p-4 border-t border-slate-700 bg-slate-800">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask about the data..."
                        className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading}
                        className="bg-indigo-600 p-2 rounded-lg hover:bg-indigo-500 disabled:opacity-50"
                    >
                        <Send size={18} className="text-white" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
