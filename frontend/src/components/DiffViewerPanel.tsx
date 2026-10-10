import React, { useState } from 'react';
import { DiffEditor } from '@monaco-editor/react';
import {
  Check,
  X,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  AlertTriangle,
} from 'lucide-react';
import type { CorrectionProposal } from '../types';

interface DiffViewerPanelProps {
  originalCode: string;
  proposals: CorrectionProposal[];
  onAcceptProposal: (proposal: CorrectionProposal) => void;
  onRejectProposal: (proposal: CorrectionProposal) => void;
  isApplying: boolean;
}

export const DiffViewerPanel: React.FC<DiffViewerPanelProps> = ({
  originalCode,
  proposals,
  onAcceptProposal,
  onRejectProposal,
  isApplying,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (proposals.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-slate-950 rounded-xl border border-slate-800 p-8 text-center">
        <Sparkles className="w-12 h-12 text-slate-600 mb-3" />
        <h3 className="text-base font-semibold text-slate-300">No Correction Proposals</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-sm">
          Click <span className="text-cyan-400 font-semibold">Auto Correct</span> to generate
          AI-assisted syntax correction proposals and preview diffs.
        </p>
      </div>
    );
  }

  const currentProposal = proposals[Math.min(currentIndex, proposals.length - 1)];
  const isSyntaxValidated = currentProposal.validation_status === 'syntax_validated';

  return (
    <div className="h-full flex flex-col bg-slate-950 rounded-xl overflow-hidden border border-slate-800 shadow-xl">
      {/* Proposal Navigation & Review Bar */}
      <div className="bg-slate-900 border-b border-slate-800 p-4 flex flex-wrap items-center justify-between gap-4">
        {/* Left: Summary & Metadata */}
        <div className="flex-1 min-w-[280px]">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
              Proposal {currentIndex + 1} of {proposals.length}
            </span>

            {isSyntaxValidated ? (
              <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Syntax Validated
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                {currentProposal.validation_status}
              </span>
            )}

            {currentProposal.confidence !== undefined && currentProposal.confidence !== null && (
              <span className="text-xs text-slate-400">
                Confidence: {(currentProposal.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>

          <h3 className="text-sm font-semibold text-white mt-1.5">{currentProposal.summary}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{currentProposal.explanation}</p>
        </div>

        {/* Right: Actions & Pagination */}
        <div className="flex items-center gap-3">
          {/* Proposal Pagination */}
          {proposals.length > 1 && (
            <div className="flex items-center gap-1 bg-slate-800 rounded-lg p-1 border border-slate-700">
              <button
                onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
                disabled={currentIndex === 0}
                className="p-1 rounded text-slate-300 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                title="Previous proposal"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs text-slate-400 px-2 font-mono">
                {currentIndex + 1} / {proposals.length}
              </span>
              <button
                onClick={() => setCurrentIndex((prev) => Math.min(proposals.length - 1, prev + 1))}
                disabled={currentIndex === proposals.length - 1}
                className="p-1 rounded text-slate-300 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                title="Next proposal"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Action Buttons */}
          <button
            onClick={() => onRejectProposal(currentProposal)}
            disabled={isApplying}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-rose-950 hover:border-rose-800 hover:text-rose-300 text-slate-300 border border-slate-700 text-xs font-semibold transition-all active:scale-95"
          >
            <X className="w-4 h-4" />
            <span>Reject</span>
          </button>

          <button
            onClick={() => onAcceptProposal(currentProposal)}
            disabled={isApplying}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all active:scale-95"
          >
            {isApplying ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Check className="w-4 h-4" />
            )}
            <span>Accept Correction</span>
          </button>
        </div>
      </div>

      {/* Diff Editor Headers */}
      <div className="grid grid-cols-2 bg-slate-900/60 px-4 py-1.5 border-b border-slate-800 text-xs text-slate-400 font-mono">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-rose-500 inline-block" />
          <span>Original Source</span>
        </div>
        <div className="flex items-center gap-2 pl-4 border-l border-slate-800">
          <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
          <span>Proposed Correction</span>
        </div>
      </div>

      {/* Diff Editor */}
      <div className="flex-1 w-full min-h-[400px]">
        <DiffEditor
          height="100%"
          language="c"
          theme="vs-dark"
          original={originalCode}
          modified={currentProposal.corrected_source}
          options={{
            readOnly: true,
            fontSize: 14,
            fontFamily: "'Fira Code', 'Cascadia Code', Consolas, monospace",
            minimap: { enabled: false },
            renderSideBySide: true,
            automaticLayout: true,
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>
    </div>
  );
};
