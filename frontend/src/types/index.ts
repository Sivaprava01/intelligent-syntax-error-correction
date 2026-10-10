export interface Diagnostic {
  code: string;
  category: 'lexical' | 'syntax' | 'semantic' | string;
  severity: 'error' | 'warning' | 'info' | string;
  message: string;
  line: number;
  column: number;
  start_offset: number;
  end_offset: number;
  excerpt?: string | null;
  recovery_status?: string | null;
}

export interface TokenInfo {
  type: string;
  type_name: string;
  value: string;
  line: number;
  column: number;
  start_offset: number;
  end_offset: number;
}

export interface EditOperation {
  operation: 'insert' | 'delete' | 'replace' | string;
  start_offset: number;
  end_offset: number;
  replacement: string;
  expected_text?: string | null;
}

export interface CorrectionProposal {
  candidate_id: string;
  summary: string;
  explanation: string;
  edit_operations: EditOperation[];
  corrected_source: string;
  validation_status:
    | 'proposed'
    | 'syntax_validated'
    | 'rejected_invalid_edit'
    | 'rejected_syntax_invalid'
    | 'unverified'
    | 'ai_unavailable'
    | string;
  related_diagnostics: string[];
  confidence?: number | null;
  ranking_score?: number | null;
  warnings?: string[];
  remaining_error_count?: number | null;
}

export interface AnalysisResponse {
  success: boolean;
  is_valid: boolean;
  error_count: number;
  warning_count: number;
  diagnostics: Diagnostic[];
  tokens: TokenInfo[];
  ast?: Record<string, unknown> | null;
}

export interface CorrectionResponse {
  success: boolean;
  source_version: string;
  is_valid: boolean;
  error_count: number;
  diagnostics: Diagnostic[];
  proposals: CorrectionProposal[];
  ai_available: boolean;
}

export interface ApplyProposalResponse {
  success: boolean;
  updated_source: string;
  new_source_version: string;
  is_valid: boolean;
  error_count: number;
  diagnostics: Diagnostic[];
  error_message?: string | null;
}

export interface HealthStatus {
  status: string;
  version: string;
  phase: string;
}
