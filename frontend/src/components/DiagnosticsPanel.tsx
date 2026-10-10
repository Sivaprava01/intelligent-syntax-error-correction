import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, ChevronRight, Terminal } from 'lucide-react';
import type { Diagnostic } from '../types';

interface DiagnosticsPanelProps {
  diagnostics: Diagnostic[];
  onSelectLine: (line: number) => void;
  isValid: boolean | null;
  isAnalyzing: boolean;
}

export const DiagnosticsPanel: React.FC<DiagnosticsPanelProps> = ({
  diagnostics,
  onSelectLine,
  isValid,
  isAnalyzing,
}) => {
  return (
    <div className="h-full flex flex-col bg-slate-950 rounded-xl overflow-hidden border border-slate-800 shadow-xl">
      {/* Header */}
      <div className="bg-slate-900/90 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-semibold text-slate-200">Compiler Diagnostics</h2>
        </div>
        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
          {diagnostics.length} {diagnostics.length === 1 ? 'item' : 'items'}
        </span>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isAnalyzing && (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400 space-y-3">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs">Running deterministic compiler analysis...</p>
          </div>
        )}

        {!isAnalyzing && isValid === true && (
          <div className="flex flex-col items-center justify-center h-48 text-center p-6 bg-emerald-950/20 border border-emerald-900/40 rounded-xl">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mb-2" />
            <h3 className="text-sm font-semibold text-emerald-300">Clean Syntax</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-xs">
              The compiler engine found 0 syntax errors in the supported C language subset.
            </p>
          </div>
        )}

        {!isAnalyzing && isValid === null && diagnostics.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-center p-6 text-slate-500">
            <p className="text-sm font-medium text-slate-400">Ready for Analysis</p>
            <p className="text-xs mt-1">
              Click <span className="text-indigo-400 font-semibold">Detect Errors</span> to analyze
              C source code.
            </p>
          </div>
        )}

        {!isAnalyzing &&
          diagnostics.map((diag, index) => {
            const isError = diag.severity === 'error';
            return (
              <div
                key={`${diag.code}-${diag.line}-${diag.column}-${index}`}
                onClick={() => onSelectLine(diag.line)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer group ${
                  isError
                    ? 'bg-rose-950/30 border-rose-900/40 hover:border-rose-700/60 hover:bg-rose-950/40'
                    : 'bg-amber-950/30 border-amber-900/40 hover:border-amber-700/60 hover:bg-amber-950/40'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {isError ? (
                      <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    )}
                    <span
                      className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                        isError
                          ? 'bg-rose-900/60 text-rose-200 border border-rose-800'
                          : 'bg-amber-900/60 text-amber-200 border border-amber-800'
                      }`}
                    >
                      {diag.code}
                    </span>
                    <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
                      {diag.category}
                    </span>
                  </div>

                  <span className="text-xs font-mono text-slate-400 group-hover:text-slate-200 flex items-center gap-1">
                    Line {diag.line}:{diag.column}
                    <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </span>
                </div>

                <p className="text-sm font-medium text-slate-200 mt-2">{diag.message}</p>

                {diag.excerpt && (
                  <div className="mt-2.5 p-2 rounded bg-slate-900/90 border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto">
                    <code>{diag.excerpt}</code>
                  </div>
                )}

                {diag.recovery_status && (
                  <div className="mt-2 flex items-center gap-1.5 text-[11px] text-slate-400">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                    <span>Recovery: {diag.recovery_status}</span>
                  </div>
                )}
              </div>
            );
          })}
      </div>
    </div>
  );
};
