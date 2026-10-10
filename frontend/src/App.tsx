import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Toolbar } from './components/Toolbar';
import { CodeEditorPanel } from './components/CodeEditorPanel';
import { DiagnosticsPanel } from './components/DiagnosticsPanel';
import { DiffViewerPanel } from './components/DiffViewerPanel';
import { NotificationBanner } from './components/NotificationBanner';
import type { NotificationState } from './components/NotificationBanner';
import { SAMPLE_PROGRAMS } from './constants/samples';
import type { SampleProgram } from './constants/samples';
import {
  checkHealth,
  analyzeCode,
  requestCorrections,
  applyCorrection,
  ApiError,
} from './services/api';
import type { Diagnostic, CorrectionProposal, HealthStatus } from './types';

export const App: React.FC = () => {
  // State
  const defaultSample = SAMPLE_PROGRAMS[0];
  const [code, setCode] = useState<string>(defaultSample.code);
  const [originalCode, setOriginalCode] = useState<string>(defaultSample.code);
  const [sourceVersion, setSourceVersion] = useState<string>('');

  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [proposals, setProposals] = useState<CorrectionProposal[]>([]);
  const [isValid, setIsValid] = useState<boolean | null>(null);

  const [activeView, setActiveView] = useState<'editor' | 'diff'>('editor');
  const [targetLine, setTargetLine] = useState<number | null>(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isCorrecting, setIsCorrecting] = useState(false);
  const [isApplying, setIsApplying] = useState(false);

  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [notification, setNotification] = useState<NotificationState | null>(null);

  // Check health on mount
  useEffect(() => {
    let mounted = true;
    checkHealth()
      .then((data) => {
        if (mounted) {
          setHealth(data);
          setHealthLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setHealth(null);
          setHealthLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  // Handlers
  const handleDetectErrors = async () => {
    if (!code.trim()) {
      setNotification({ type: 'warning', message: 'Editor is empty. Please enter C source code.' });
      return;
    }

    setIsAnalyzing(true);
    setNotification(null);

    try {
      const res = await analyzeCode(code);
      setDiagnostics(res.diagnostics);
      setIsValid(res.is_valid);

      if (res.is_valid) {
        setNotification({
          type: 'success',
          message: 'Syntax analysis passed! 0 syntax errors detected.',
        });
      } else {
        setNotification({
          type: 'warning',
          message: `Compiler engine detected ${res.error_count} syntax error${
            res.error_count === 1 ? '' : 's'
          }. Click 'Auto Correct' to view proposed repairs.`,
        });
      }
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Error analyzing source code.';
      setNotification({ type: 'error', message: msg });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAutoCorrect = async () => {
    if (!code.trim()) {
      setNotification({ type: 'warning', message: 'Editor is empty. Please enter C source code.' });
      return;
    }

    setIsCorrecting(true);
    setNotification(null);

    try {
      const res = await requestCorrections(code);
      setDiagnostics(res.diagnostics);
      setIsValid(res.is_valid);
      setSourceVersion(res.source_version);
      setProposals(res.proposals);

      if (res.is_valid) {
        setNotification({
          type: 'info',
          message: 'Code is already syntactically valid! No corrections needed.',
        });
      } else if (res.proposals.length > 0) {
        setNotification({
          type: 'success',
          message: `Generated and validated ${res.proposals.length} correction proposal${
            res.proposals.length === 1 ? '' : 's'
          }. Previewing diff...`,
        });
        setActiveView('diff');
      } else {
        setNotification({
          type: 'warning',
          message: 'No suitable correction proposals could be validated for this syntax.',
        });
      }
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Error generating corrections.';
      setNotification({ type: 'error', message: msg });
    } finally {
      setIsCorrecting(false);
    }
  };

  const handleAcceptProposal = async (proposal: CorrectionProposal) => {
    setIsApplying(true);
    setNotification(null);

    try {
      const res = await applyCorrection(code, sourceVersion, proposal);

      if (res.success) {
        setCode(res.updated_source);
        setSourceVersion(res.new_source_version);
        setDiagnostics(res.diagnostics);
        setIsValid(res.is_valid);

        // Remove applied proposal from active list
        const remaining = proposals.filter((p) => p.candidate_id !== proposal.candidate_id);
        setProposals(remaining);

        setNotification({
          type: 'success',
          message:
            res.is_valid
              ? 'Correction applied successfully! Code now passes deterministic syntax analysis.'
              : `Correction applied. ${res.error_count} remaining error(s).`,
        });

        if (remaining.length === 0 || res.is_valid) {
          setActiveView('editor');
        }
      } else {
        setNotification({
          type: 'error',
          message: res.error_message || 'Failed to apply proposal.',
        });
      }
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Failed to apply correction.';
      setNotification({ type: 'error', message: msg });
    } finally {
      setIsApplying(false);
    }
  };

  const handleRejectProposal = (proposal: CorrectionProposal) => {
    const remaining = proposals.filter((p) => p.candidate_id !== proposal.candidate_id);
    setProposals(remaining);

    setNotification({
      type: 'info',
      message: 'Correction proposal rejected. Working source code was not modified.',
    });

    if (remaining.length === 0) {
      setActiveView('editor');
    }
  };

  const handleSelectSample = (sample: SampleProgram) => {
    setCode(sample.code);
    setOriginalCode(sample.code);
    setDiagnostics([]);
    setProposals([]);
    setIsValid(null);
    setActiveView('editor');
    setNotification({
      type: 'info',
      message: `Loaded sample: "${sample.name}"`,
    });
  };

  const handleReset = () => {
    setCode(originalCode);
    setDiagnostics([]);
    setProposals([]);
    setIsValid(null);
    setActiveView('editor');
    setNotification({
      type: 'info',
      message: 'Source code reset to original state.',
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans antialiased">
      {/* App Header */}
      <Header health={health} healthLoading={healthLoading} />

      {/* Action Toolbar */}
      <Toolbar
        onDetectErrors={handleDetectErrors}
        onAutoCorrect={handleAutoCorrect}
        onReset={handleReset}
        onSelectSample={handleSelectSample}
        isAnalyzing={isAnalyzing}
        isCorrecting={isCorrecting}
        activeView={activeView}
        setActiveView={setActiveView}
        errorCount={diagnostics.filter((d) => d.severity === 'error').length}
        proposalCount={proposals.length}
        isValid={isValid}
        hasProposals={proposals.length > 0}
      />

      {/* Notifications */}
      <NotificationBanner notification={notification} onClose={() => setNotification(null)} />

      {/* Main Workspace Layout */}
      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
        {activeView === 'editor' ? (
          <>
            {/* Code Editor Panel */}
            <div className="lg:col-span-8 flex flex-col h-[calc(100vh-210px)] min-h-[500px]">
              <CodeEditorPanel
                code={code}
                onChange={(val) => {
                  setCode(val);
                  // Clear stale diagnostics if code modified
                  if (isValid !== null) setIsValid(null);
                }}
                diagnostics={diagnostics}
                targetLine={targetLine}
              />
            </div>

            {/* Diagnostics Panel */}
            <div className="lg:col-span-4 flex flex-col h-[calc(100vh-210px)] min-h-[500px]">
              <DiagnosticsPanel
                diagnostics={diagnostics}
                onSelectLine={(line) => setTargetLine(line)}
                isValid={isValid}
                isAnalyzing={isAnalyzing}
              />
            </div>
          </>
        ) : (
          /* Side-by-Side Diff View */
          <div className="col-span-12 flex flex-col h-[calc(100vh-210px)] min-h-[500px]">
            <DiffViewerPanel
              originalCode={code}
              proposals={proposals}
              onAcceptProposal={handleAcceptProposal}
              onRejectProposal={handleRejectProposal}
              isApplying={isApplying}
            />
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
