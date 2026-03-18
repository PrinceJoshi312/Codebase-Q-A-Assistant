import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Send, 
  Terminal, 
  FolderTree, 
  Database, 
  Cpu, 
  MessageSquare, 
  AlertCircle,
  Loader2,
  Github,
  ChevronRight,
  Code2,
  Sparkles,
  Command
} from 'lucide-react';

const API_BASE = 'http://localhost:12345';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const App: React.FC = () => {
  const [repoUrl, setRepoUrl] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isIngesting, setIsIngesting] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [structure, setStructure] = useState<string>('');
  const [repoName, setRepoName] = useState<string>('');
  const [status, setStatus] = useState<{ type: 'info' | 'error' | 'success', message: string } | null>(null);
  
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl) return;

    setIsIngesting(true);
    setStatus({ type: 'info', message: 'Analyzing repository architecture...' });
    
    try {
      const response = await axios.post(`${API_BASE}/ingest`, { url: repoUrl });
      setRepoName(response.data.repo_name);
      setStatus({ type: 'success', message: `Indexed ${response.data.repo_name}` });
      
      const structRes = await axios.get(`${API_BASE}/structure`);
      setStructure(structRes.data.structure);
      
      setMessages([{ 
        role: 'assistant', 
        content: `I've successfully indexed **${response.data.repo_name}**. \n\nI've detected the entry point at \`${response.data.entry_point}\`. You can now ask me questions about the logic, architecture, or specific functions in this codebase.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } catch (err: any) {
      setStatus({ type: 'error', message: err.response?.data?.detail || 'Failed to ingest repository.' });
    } finally {
      setIsIngesting(false);
      setTimeout(() => setStatus(null), 5000);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isChatting) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: userMsg,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
    setInput('');
    setIsChatting(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, { message: userMsg });
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I encountered an error while processing your request. Please check the backend connection.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#020617] text-slate-200 overflow-hidden font-sans selection:bg-sky-500/30">
      
      {/* Sidebar */}
      <aside className="w-72 bg-[#0b1120] border-r border-slate-800/60 flex flex-col z-20">
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-sky-500 rounded-lg flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Cpu size={18} className="text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight text-white">BMAD <span className="text-sky-500">AI</span></span>
        </div>

        <div className="flex-1 overflow-y-auto px-4 space-y-8">
          {/* Ingest Section */}
          <section>
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-3 block px-2">
              Source Repository
            </label>
            <form onSubmit={handleIngest} className="space-y-2">
              <div className="relative group">
                <Github className="absolute left-3 top-2.5 text-slate-500 group-focus-within:text-sky-500 transition-colors" size={14} />
                <input 
                  type="text" 
                  placeholder="GitHub URL..." 
                  className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-2 pl-9 pr-4 text-xs focus:outline-none focus:border-sky-500/50 focus:ring-4 focus:ring-sky-500/5 transition-all placeholder:text-slate-600"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  disabled={isIngesting}
                />
              </div>
              <button 
                type="submit"
                disabled={isIngesting || !repoUrl}
                className="w-full bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 font-semibold py-2 rounded-xl text-xs transition-all flex items-center justify-center gap-2 border border-slate-700/50"
              >
                {isIngesting ? <Loader2 className="animate-spin" size={14} /> : 'Analyze Base'}
              </button>
            </form>
          </section>

          {/* Project Details */}
          {repoName && (
            <section className="animate-in fade-in slide-in-from-left-4 duration-500">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-3 block px-2">
                Active Context
              </label>
              <div className="bg-sky-500/5 border border-sky-500/10 rounded-xl p-3">
                <div className="flex items-center gap-2 text-sky-400 mb-1">
                  <Code2 size={14} />
                  <span className="text-xs font-bold truncate">{repoName}</span>
                </div>
                <p className="text-[10px] text-slate-500 flex items-center gap-1">
                  <Sparkles size={10} /> Indexed & Ready
                </p>
              </div>
            </section>
          )}

          {/* Structure */}
          {structure && (
            <section className="animate-in fade-in slide-in-from-left-4 duration-700">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-3 block px-2">
                Architecture
              </label>
              <div className="bg-slate-950/50 border border-slate-800/50 rounded-xl p-3 font-mono text-[10px] text-slate-500 leading-relaxed max-h-64 overflow-y-auto scrollbar-hide">
                {structure.split('\n').map((line, i) => (
                  <div key={i} className="whitespace-nowrap hover:text-slate-300 transition-colors">
                    {line}
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        <div className="p-4 border-t border-slate-800/60 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">System Ready</span>
          </div>
          <Command size={14} className="text-slate-600" />
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative bg-[#020617]">
        
        {/* Floating Status Toast */}
        {status && (
          <div className="absolute top-6 left-1/2 -translate-x-1/2 z-50 animate-in fade-in zoom-in slide-in-from-top-4 duration-300">
            <div className={`px-4 py-2 rounded-full text-xs font-bold flex items-center gap-3 shadow-2xl border backdrop-blur-md ${
              status.type === 'error' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
              status.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
              'bg-sky-500/10 text-sky-400 border-sky-500/20'
            }`}>
              {status.type === 'error' ? <AlertCircle size={14} /> : status.type === 'success' ? <Terminal size={14} /> : <Loader2 size={14} className="animate-spin" />}
              {status.message}
            </div>
          </div>
        )}

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto px-6 py-8 space-y-8 scroll-smooth">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-sm mx-auto space-y-4">
              <div className="w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center border border-slate-800 mb-2">
                <MessageSquare size={32} className="text-sky-500" />
              </div>
              <h2 className="text-xl font-bold text-white">Code Intelligence</h2>
              <p className="text-sm text-slate-500 leading-relaxed">
                Connect a GitHub repository to begin a deep analysis. I can explain complex logic, find optimizations, and map dependencies.
              </p>
              <div className="grid grid-cols-2 gap-2 w-full pt-4">
                {['Explain logic', 'Find bugs', 'Map architecture', 'Review code'].map(tag => (
                  <div key={tag} className="px-3 py-2 bg-slate-900/50 border border-slate-800 rounded-lg text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    {tag}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m, i) => (
              <div key={i} className={`flex gap-4 ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                <div className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center border ${
                  m.role === 'user' ? 'bg-slate-800 border-slate-700' : 'bg-sky-500/10 border-sky-500/20 text-sky-500'
                }`}>
                  {m.role === 'user' ? <Github size={14} /> : <Sparkles size={14} />}
                </div>
                <div className={`flex flex-col gap-1.5 max-w-[75%] ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`px-5 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                    m.role === 'user' 
                      ? 'bg-sky-600 text-white rounded-tr-none' 
                      : 'bg-[#0b1120] text-slate-200 border border-slate-800/60 rounded-tl-none'
                  }`}>
                    <div className="whitespace-pre-wrap">{m.content}</div>
                  </div>
                  <span className="text-[9px] font-bold text-slate-600 uppercase tracking-widest px-1">{m.timestamp}</span>
                </div>
              </div>
            ))
          )}
          {isChatting && (
            <div className="flex gap-4 animate-pulse">
              <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-500">
                <Loader2 className="animate-spin" size={14} />
              </div>
              <div className="bg-[#0b1120] border border-slate-800/60 rounded-2xl rounded-tl-none px-5 py-3">
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 bg-sky-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <div className="w-1.5 h-1.5 bg-sky-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <div className="w-1.5 h-1.5 bg-sky-500 rounded-full animate-bounce" />
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Dock */}
        <div className="p-8 pt-0">
          <div className="max-w-3xl mx-auto relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-sky-500/20 to-indigo-500/20 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-1000"></div>
            <form onSubmit={handleSend} className="relative flex items-center bg-[#0b1120] border border-slate-800 rounded-2xl shadow-2xl focus-within:border-sky-500/50 transition-all">
              <div className="pl-5 text-slate-500">
                <ChevronRight size={18} />
              </div>
              <input 
                type="text" 
                placeholder={structure ? "Ask about the code structure, functions, or logic..." : "Index a repository to start chatting..."}
                className="w-full bg-transparent border-none py-5 px-4 text-sm focus:outline-none placeholder:text-slate-600 disabled:cursor-not-allowed"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isChatting || !structure}
              />
              <div className="pr-3 flex items-center gap-2">
                <kbd className="hidden sm:flex h-6 items-center gap-1 rounded border border-slate-700 bg-slate-800 px-1.5 font-mono text-[10px] font-medium text-slate-500 opacity-100">
                  <span className="text-xs">⌘</span>Enter
                </kbd>
                <button 
                  type="submit"
                  disabled={isChatting || !input.trim() || !structure}
                  className="p-2.5 bg-sky-500 text-white rounded-xl hover:bg-sky-400 disabled:bg-slate-800 disabled:text-slate-600 transition-all shadow-lg shadow-sky-500/10"
                >
                  <Send size={18} />
                </button>
              </div>
            </form>
          </div>
          <p className="text-center text-[9px] font-bold text-slate-700 mt-4 uppercase tracking-[0.3em]">
            Optimized for Gemini 2.5 Flash Neural Engine
          </p>
        </div>
      </main>
    </div>
  );
};

export default App;
