import React from 'react';
import {
  Play,
  Sparkles,
  RotateCcw,
  BookOpen,
  GitCompare,
  Code2,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { SAMPLE_PROGRAMS } from '../constants/samples';
import type { SampleProgram } from '../constants/samples';

interface ToolbarProps {
  onDetectErrors: () => void;
  onAutoCorrect: () => void;
  onReset: () => void;
  onSelectSample: (sample: SampleProgram) => void;
  isAnalyzing: boolean;
  isCorrecting: boolean;
  activeView: 'editor' | 'diff';
  setActiveView: (view: 'editor' | 'diff') => void;
  errorCount: number;
  proposalCount: number;
  isValid: boolean | null;
  hasProposals: boolean;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  onDetectErrors,
  onAutoCorrect,
  onReset,
  onSelectSample,
  isAnalyzing,
  isCorrecting,
  activeView,
  setActiveView,
  errorCount,
  proposalCount,
  isValid,
  hasProposals,
}) => {
  return (
    <div className="bg-slate-900 border-b border-slate-800 px-6 py-2.5 flex flex-wrap items-center justify-between gap-3">
      {/* Action Buttons */}
      <div className="flex items-center gap-2.5 flex-wrap">
        <button
          onClick={onDetectErrors}
          disabled={isAnalyzing || isCorrecting}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium shadow-md shadow-indigo-600/20 transition-all active:scale-[0.98]"
        >
          {isAnalyzing ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Play className="w-4 h-4 fill-white" />
          )}
          <span>Detect Errors</span>
        </button>

        <button
          onClick={onAutoCorrect}
          disabled={isAnalyzing || isCorrecting}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium shadow-md shadow-cyan-600/20 transition-all active:scale-[0.98]"
        >
          {isCorrecting ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
          <span>Auto Correct</span>
        </button>

        <button
          onClick={onReset}
          disabled={isAnalyzing || isCorrecting}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium border border-slate-700 transition-all"
          title="Reset to original code"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset</span>
        </button>

        {/* Sample selector */}
        <div className="relative inline-flex items-center">
          <BookOpen className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
          <select
            onChange={(e) => {
              const sample = SAMPLE_PROGRAMS.find((s) => s.id === e.target.value);
              if (sample) onSelectSample(sample);
            }}
            defaultValue=""
            className="pl-9 pr-8 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm border border-slate-700 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500 appearance-none transition-all"
          >
            <option value="" disabled>
              Load Sample C Code...
            </option>
            {SAMPLE_PROGRAMS.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* View Switcher & Stats */}
      <div className="flex items-center gap-3">
        {/* Status Indicators */}
        {isValid === true && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/80 border border-emerald-700/60 text-emerald-300 text-xs font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>0 Errors (Valid C Subset)</span>
          </div>
        )}

        {isValid === false && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-950/80 border border-rose-700/60 text-rose-300 text-xs font-semibold">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
            <span>{errorCount} Syntax Error{errorCount === 1 ? '' : 's'}</span>
          </div>
        )}

        {proposalCount > 0 && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/80 border border-cyan-700/60 text-cyan-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>{proposalCount} Proposal{proposalCount === 1 ? '' : 's'}</span>
          </div>
        )}

        {/* View Toggle */}
        <div className="flex items-center p-1 rounded-lg bg-slate-950 border border-slate-800 text-xs">
          <button
            onClick={() => setActiveView('editor')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
              activeView === 'editor'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Editor & Diagnostics</span>
          </button>
          <button
            onClick={() => setActiveView('diff')}
            disabled={!hasProposals}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
              !hasProposals
                ? 'opacity-40 cursor-not-allowed text-slate-500'
                : activeView === 'diff'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <GitCompare className="w-3.5 h-3.5" />
            <span>Side-by-Side Diff</span>
          </button>
        </div>
      </div>
    </div>
  );
};
