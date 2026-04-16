import React from 'react';
import { FileCode, Folder, ChevronDown } from 'lucide-react';

interface StructureViewProps {
  structure: string;
}

const StructureView: React.FC<StructureViewProps> = ({ structure }) => {
  if (!structure) return null;

  return (
    <section className="animate-in fade-in slide-in-from-left-4 duration-700">
      <div className="flex items-center justify-between mb-4">
        <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">
          Architecture
        </label>
        <ChevronDown size={12} className="text-slate-700" />
      </div>
      <div className="bg-black/40 border border-white/5 rounded-2xl p-4 font-mono text-[10px] text-slate-500 leading-relaxed max-h-80 overflow-y-auto scrollbar-hide backdrop-blur-sm">
        {structure.split('\n').map((line, i) => {
          const isFile = line.includes('.') && !line.endsWith('/');
          const indent = line.search(/\S/);
          
          if (line.trim() === "") return null;

          return (
            <div key={i} className="flex items-center gap-2.5 py-1 hover:text-indigo-400 transition-colors group cursor-default">
              <span className="flex-shrink-0" style={{ marginLeft: `${indent * 4}px` }}>
                {isFile ? (
                  <FileCode size={12} className="text-slate-700 group-hover:text-indigo-500 transition-colors" />
                ) : (
                  <Folder size={12} className="text-indigo-500/30 group-hover:text-indigo-500 transition-colors" />
                )}
              </span>
              <span className="truncate tracking-tight font-medium">{line.trim()}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default StructureView;
