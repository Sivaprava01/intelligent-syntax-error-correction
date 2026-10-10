import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import type { OnMount } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import type { Diagnostic } from '../types';

interface CodeEditorPanelProps {
  code: string;
  onChange: (newCode: string) => void;
  diagnostics: Diagnostic[];
  targetLine: number | null;
}

export const CodeEditorPanel: React.FC<CodeEditorPanelProps> = ({
  code,
  onChange,
  diagnostics,
  targetLine,
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof import('monaco-editor') | null>(null);

  const handleEditorDidMount: OnMount = (editorInstance, monacoInstance) => {
    editorRef.current = editorInstance;
    monacoRef.current = monacoInstance as unknown as typeof import('monaco-editor');
  };

  // Update Monaco diagnostic markers whenever diagnostics change
  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) return;

    const model = editorRef.current.getModel();
    if (!model) return;

    const markers: editor.IMarkerData[] = diagnostics.map((diag) => ({
      startLineNumber: Math.max(1, diag.line),
      startColumn: Math.max(1, diag.column),
      endLineNumber: Math.max(1, diag.line),
      endColumn: Math.max(1, diag.column + 1),
      message: `[${diag.code}] ${diag.message}`,
      severity:
        diag.severity === 'error'
          ? monacoRef.current!.MarkerSeverity.Error
          : monacoRef.current!.MarkerSeverity.Warning,
    }));

    monacoRef.current.editor.setModelMarkers(model, 'compiler', markers);
  }, [diagnostics]);

  // Jump to targeted line if user clicked diagnostic item
  useEffect(() => {
    if (targetLine && editorRef.current) {
      editorRef.current.revealLineInCenter(targetLine);
      editorRef.current.setPosition({ lineNumber: targetLine, column: 1 });
      editorRef.current.focus();
    }
  }, [targetLine]);

  return (
    <div className="h-full w-full flex flex-col bg-slate-950 rounded-xl overflow-hidden border border-slate-800 shadow-xl">
      <div className="bg-slate-900/90 px-4 py-2 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-2 font-mono">
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 inline-block" />
          <span>source.c</span>
        </div>
        <span>C Language (C99 Subset)</span>
      </div>
      <div className="flex-1 w-full min-h-[400px]">
        <Editor
          height="100%"
          defaultLanguage="c"
          language="c"
          theme="vs-dark"
          value={code}
          onChange={(val) => onChange(val || '')}
          onMount={handleEditorDidMount}
          options={{
            fontSize: 14,
            fontFamily: "'Fira Code', 'Cascadia Code', Consolas, monospace",
            minimap: { enabled: false },
            lineNumbers: 'on',
            roundedSelection: true,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            renderWhitespace: 'selection',
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>
    </div>
  );
};
