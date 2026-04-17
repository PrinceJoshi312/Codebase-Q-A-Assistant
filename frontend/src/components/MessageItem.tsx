import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Github, Sparkles } from 'lucide-react';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const MessageItem: React.FC<MessageProps> = ({ role, content, timestamp }) => {
  return (
    <div className={`flex gap-6 ${role === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-in fade-in slide-in-from-bottom-4 duration-500`}>
      <div className={`w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center border shadow-lg ${
        role === 'user' 
          ? 'bg-slate-900 border-white/10 text-slate-400' 
          : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400 shadow-indigo-500/5'
      }`}>
        {role === 'user' ? <Github size={18} /> : <Sparkles size={18} />}
      </div>
      <div className={`flex flex-col gap-2 max-w-[85%] ${role === 'user' ? 'items-end' : 'items-start'}`}>
        <div className={`px-6 py-4 rounded-[2rem] text-sm leading-relaxed shadow-2xl backdrop-blur-sm ${
          role === 'user' 
            ? 'bg-indigo-600 text-white rounded-tr-none font-medium' 
            : 'bg-[#0a0a0a] text-slate-200 border border-white/10 rounded-tl-none'
        }`}>
          <div className="prose prose-invert prose-indigo max-w-none">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }: any) {
                  return !inline ? (
                    <div className="relative group my-4">
                      <div className="absolute -inset-2 bg-indigo-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                      <pre className="relative bg-black/50 p-5 rounded-2xl border border-white/5 overflow-x-auto font-mono text-xs leading-normal">
                        <code className={className} {...props}>
                          {children}
                        </code>
                      </pre>
                    </div>
                  ) : (
                    <code className="bg-white/5 px-2 py-0.5 rounded-md text-indigo-300 font-mono text-xs border border-white/5" {...props}>
                      {children}
                    </code>
                  );
                },
                p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
                h3: ({ children }) => <h3 className="text-white font-black text-lg mb-4 tracking-tight">{children}</h3>,
                ul: ({ children }) => <ul className="list-disc ml-4 mb-4 space-y-2">{children}</ul>,
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </div>
        <span className="text-[10px] font-black text-slate-700 uppercase tracking-[0.2em] px-2">{timestamp}</span>
      </div>
    </div>
  );
};

export default MessageItem;
