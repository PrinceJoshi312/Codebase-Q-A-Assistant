import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Cpu, 
  MessageSquare, 
  AlertCircle,
  Loader2,
  Github,
  ChevronRight,
  Code2,
  Sparkles,
  Command,
  LayoutDashboard,
  Zap,
  ShieldCheck,
  Globe
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import MessageItem from './components/MessageItem';
import StructureView from './components/StructureView';
import SplashScreen from './components/SplashScreen';

// Utility for cleaner classes
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const API_BASE = '';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const SUGGESTIONS = [
  { label: 'Explain Logic', icon: Zap },
  { label: 'Find Bugs', icon: AlertCircle },
  { label: 'Map Architecture', icon: Code2 },
  { label: 'Review Security', icon: ShieldCheck }
];

const App: React.FC = () => {
  const [showSplash, setShowSplash] = useState(true);
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
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isChatting]);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl) return;

    setIsIngesting(true);
    setStatus({ type: 'info', message: 'Synchronizing with Neural Engine...' });
    
    try {
      const response = await axios.post(`${API_BASE}/ingest`, { url: repoUrl });
      setRepoName(response.data.repo_name);
      setStatus({ type: 'success', message: `Indexed ${response.data.repo_name}` });
      
      const structRes = await axios.get(`${API_BASE}/structure`);
      setStructure(structRes.data.structure);
      
      setMessages([{ 
        role: 'assistant', 
        content: `### 🧠 Repository Synchronized\n\nI have completed the neural mapping of **${response.data.repo_name}**.\n\n*   **Entry Point Detected**: \`${response.data.entry_point}\`\n*   **Total Files**: ${response.data.file_count}\n\nI am ready to provide architectural insights. You can use the quick-action tags below or ask a specific question.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } catch (err: any) {
      console.error(err);
      setStatus({ type: 'error', message: err.response?.data?.detail || 'Engine Error: Connection Refused.' });
    } finally {
      setIsIngesting(false);
      setTimeout(() => setStatus(null), 5000);
    }
  };

  const handleSend = async (e: React.FormEvent | string) => {
    // If e is a string, it's from a suggestion button
    const text = typeof e === 'string' ? e : input;
    
    // Prevent default if it's a form event
    if (typeof e !== 'string') {
      e.preventDefault();
    }

    if (!text.trim() || isChatting) return;

    const userMsg = text.trim();
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: userMsg,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
    
    // Clear input IF we submitted via form OR button
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
        content: "**Error:** The Neural Engine (Backend) is offline or the API key is invalid. Please check the terminal logs.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <>
      <AnimatePresence>
        {showSplash && <SplashScreen />}
      </AnimatePresence>

      <div className="flex h-screen bg-black text-slate-300 overflow-hidden font-sans selection:bg-indigo-500/30">
      
      {/* Sidebar Navigation */}
      <aside className="w-20 lg:w-72 bg-[#0a0a0a] border-r border-white/5 flex flex-col z-30 transition-all duration-300">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Cpu size={20} className="text-white" />
          </div>
          <span className="font-black text-lg tracking-tighter text-white hidden lg:block uppercase leading-none">Codebase Neural <br/><span className="text-indigo-500">Assistant</span></span>
        </div>

        <nav className="flex-1 px-4 mt-4 space-y-2">
          <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-semibold bg-white/5 text-white transition-all group">
            <LayoutDashboard size={20} className="text-indigo-500" />
            <span className="hidden lg:block">Active Session</span>
          </button>
        </nav>

        <div className="p-4 mt-auto">
          <div className="bg-gradient-to-b from-indigo-500/10 to-transparent rounded-2xl p-4 border border-indigo-500/20 hidden lg:block">
            <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2 text-center">Engine Status</h4>
            <p className="text-[10px] text-slate-500 leading-relaxed mb-3 text-center font-bold">Gemini 2.5 Flash Pro optimized for code analysis.</p>
            <div className="flex items-center justify-center gap-2 py-1.5 bg-emerald-500/5 rounded-lg border border-emerald-500/20">
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-[9px] font-bold text-emerald-400 uppercase tracking-[0.2em]">System Online</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Repository & Context Column */}
      <aside className="w-80 bg-[#080808] border-r border-white/5 hidden xl:flex flex-col z-20 overflow-y-auto scrollbar-hide">
        <div className="p-6 space-y-8">
          <section>
            <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] block mb-4">
              Source Entry
            </label>
            <form onSubmit={handleIngest} className="space-y-3">
              <div className="relative group">
                <Github className="absolute left-3 top-3 text-slate-600 group-focus-within:text-indigo-500 transition-colors" size={16} />
                <input 
                  type="text" 
                  placeholder="Paste GitHub URL..." 
                  className="w-full bg-black border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs focus:outline-none focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 transition-all placeholder:text-slate-700 font-medium"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  disabled={isIngesting}
                />
              </div>
              <button 
                type="submit"
                disabled={isIngesting || !repoUrl}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white font-bold py-3 rounded-xl text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 active:scale-95"
              >
                {isIngesting ? <Loader2 className="animate-spin" size={16} /> : <><Sparkles size={14} /> Analyze Codebase</>}
              </button>
            </form>
          </section>

          <AnimatePresence>
            {repoName && (
              <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">
                  Environment
                </label>
                <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
                  <div className="flex items-center gap-3 mb-2 text-white">
                    <Code2 size={16} className="text-indigo-400" />
                    <span className="text-xs font-bold truncate">{repoName}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Globe size={10} className="text-slate-600" />
                    <span className="text-[9px] text-slate-500 uppercase font-bold tracking-tighter">Production Node</span>
                  </div>
                </div>
              </motion.section>
            )}
          </AnimatePresence>

          <StructureView structure={structure} />
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="flex-1 flex flex-col relative bg-black">
        
        {/* Header Bar */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-black/80 backdrop-blur-xl z-10">
          <div className="flex items-center gap-4">
            <div className="px-2 py-1 bg-white/5 rounded-md border border-white/10 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              Live Session
            </div>
            <div className="h-4 w-px bg-white/10" />
          </div>
        </header>

        {/* Status Notification */}
        <AnimatePresence>
          {status && (
            <motion.div initial={{ opacity: 0, y: -20, x: '-50%' }} animate={{ opacity: 1, y: 0, x: '-50%' }} exit={{ opacity: 0, y: -20, x: '-50%' }} className="absolute top-20 left-1/2 z-50 pointer-events-none">
              <div className={cn(
                "px-6 py-3 rounded-2xl text-xs font-bold flex items-center gap-3 shadow-2xl border backdrop-blur-2xl",
                status.type === 'error' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                status.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
              )}>
                {status.type === 'error' ? <AlertCircle size={16} /> : status.type === 'success' ? <Sparkles size={16} /> : <Loader2 size={16} className="animate-spin" />}
                {status.message}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-6 lg:px-20 py-12 space-y-12 scroll-smooth scrollbar-hide">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto text-center space-y-8">
              <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="w-24 h-24 bg-indigo-500/10 rounded-[2.5rem] flex items-center justify-center border border-white/5">
                <MessageSquare size={48} className="text-indigo-500" />
              </motion.div>
              <div className="space-y-4">
                <h2 className="text-4xl font-black text-white tracking-tighter">Neural Code <span className="text-indigo-500">Reasoning</span></h2>
                <p className="text-slate-400 text-lg leading-relaxed font-medium">Connect a repository to analyze complex logic and architecture.</p>
              </div>
            </div>
          ) : (
            messages.map((m, i) => (
              <MessageItem key={i} role={m.role} content={m.content} timestamp={m.timestamp} />
            ))
          )}
          {isChatting && (
            <div className="flex gap-6 animate-pulse px-4">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-500">
                <Loader2 className="animate-spin" size={18} />
              </div>
              <div className="bg-white/5 border border-white/10 rounded-3xl rounded-tl-none px-6 py-4">
                <div className="flex gap-1.5">
                  <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" />
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Dock */}
        <div className="px-6 lg:px-20 pb-12">
          {/* Quick Action Tags */}
          <div className="max-w-4xl mx-auto flex flex-wrap gap-2 mb-4 justify-center">
            {SUGGESTIONS.map((tag) => (
              <button 
                key={tag.label}
                onClick={() => handleSend(tag.label)}
                disabled={!structure || isChatting}
                className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black text-slate-500 uppercase tracking-widest hover:border-indigo-500/30 hover:text-indigo-400 transition-all disabled:opacity-30 flex items-center gap-2"
              >
                <tag.icon size={12} />
                {tag.label}
              </button>
            ))}
          </div>

          <div className="max-w-4xl mx-auto relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-violet-600 rounded-[2rem] blur opacity-10 group-focus-within:opacity-25 transition duration-1000"></div>
            <form onSubmit={handleSend} className="relative flex items-center bg-[#0a0a0a] border border-white/10 rounded-[1.5rem] shadow-3xl focus-within:border-indigo-500/50 transition-all overflow-hidden p-1">
              <div className="pl-6 text-slate-600">
                <ChevronRight size={24} />
              </div>
              <input 
                type="text" 
                placeholder={structure ? "Ask the Neural Engine about the codebase..." : "Analyze a repository to start chatting..."}
                className="w-full bg-transparent border-none py-6 px-6 text-sm lg:text-base focus:outline-none placeholder:text-slate-700 disabled:cursor-not-allowed font-medium text-white"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isChatting || !structure}
              />
              <div className="pr-4 flex items-center gap-4">
                <button 
                  type="submit"
                  disabled={isChatting || !input.trim() || !structure}
                  className="p-4 bg-indigo-600 text-white rounded-2xl hover:bg-indigo-500 disabled:bg-white/5 disabled:text-slate-800 transition-all shadow-xl shadow-indigo-600/10 active:scale-95"
                >
                  <Send size={20} />
                </button>
              </div>
            </form>
          </div>
          <p className="text-center text-[9px] font-black text-slate-800 mt-6 uppercase tracking-[0.5em]">
            Optimized for Gemini 2.5 Flash Stable Pipeline
          </p>
        </div>
      </main>
    </div>
    </>
  );
};

export default App;
