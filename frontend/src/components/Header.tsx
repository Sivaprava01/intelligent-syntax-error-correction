import React from 'react';
import { Terminal, ShieldCheck, AlertCircle } from 'lucide-react';
import type { HealthStatus } from '../types';

interface HeaderProps {
  health: HealthStatus | null;
  healthLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({ health, healthLoading }) => {
  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-cyan-500 to-emerald-400 p-0.5 shadow-lg shadow-indigo-500/20">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <Terminal className="w-5 h-5 text-cyan-400" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-tight">
              Intelligent C Syntax Error Detector & Auto-Corrector
            </h1>
            <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
              Phase 3
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Deterministic Compiler Engine + AI-Assisted Correction & Verification
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {healthLoading ? (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs text-slate-400">
            <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            Connecting to compiler backend...
          </div>
        ) : health?.status === 'ok' ? (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-xs text-emerald-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Compiler Engine v{health.version} Online</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-950/60 border border-rose-800/60 text-xs text-rose-300">
            <AlertCircle className="w-4 h-4 text-rose-400" />
            <span>Backend Offline</span>
          </div>
        )}
      </div>
    </header>
  );
};
