import { describe, it, expect, vi, beforeEach } from 'vitest';
import { checkHealth, analyzeCode, requestCorrections, applyCorrection, ApiError } from '../services/api';
import type { CorrectionProposal } from '../types';

describe('Frontend API Services', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('checkHealth parses successful backend response', async () => {
    const mockHealth = { status: 'ok', version: '2.0.0', phase: 'Phase 2' };
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockHealth,
    } as Response);

    const health = await checkHealth();
    expect(health.status).toBe('ok');
    expect(health.version).toBe('2.0.0');
  });

  it('analyzeCode handles syntax error response', async () => {
    const mockAnalysis = {
      success: true,
      is_valid: false,
      error_count: 1,
      warning_count: 0,
      diagnostics: [
        {
          code: 'E203',
          category: 'syntax',
          severity: 'error',
          message: "Expected ';' after variable declaration",
          line: 2,
          column: 15,
          start_offset: 20,
          end_offset: 22,
        },
      ],
      tokens: [],
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysis,
    } as Response);

    const result = await analyzeCode('int main() { int a = 10 return a; }');
    expect(result.is_valid).toBe(false);
    expect(result.error_count).toBe(1);
    expect(result.diagnostics[0].code).toBe('E203');
  });

  it('requestCorrections returns proposals', async () => {
    const mockProposal: CorrectionProposal = {
      candidate_id: 'cand_123',
      summary: 'Insert semicolon',
      explanation: 'Fix missing delimiter',
      edit_operations: [
        { operation: 'insert', start_offset: 22, end_offset: 22, replacement: ';' },
      ],
      corrected_source: 'int main() { int a = 10; return a; }',
      validation_status: 'syntax_validated',
      related_diagnostics: ['E203'],
    };

    const mockResponse = {
      success: true,
      source_version: 'hash123',
      is_valid: false,
      error_count: 1,
      diagnostics: [],
      proposals: [mockProposal],
      ai_available: true,
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response);

    const result = await requestCorrections('int main() { int a = 10 return a; }');
    expect(result.proposals).toHaveLength(1);
    expect(result.proposals[0].validation_status).toBe('syntax_validated');
  });

  it('applyCorrection handles stale proposal error', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: false,
        updated_source: 'int x = 1;',
        new_source_version: 'v1',
        is_valid: false,
        error_count: 1,
        diagnostics: [],
        error_message: 'Stale proposal: source version mismatch',
      }),
    } as Response);

    const mockProposal: CorrectionProposal = {
      candidate_id: 'c_stale',
      summary: 'Fix',
      explanation: '',
      edit_operations: [],
      corrected_source: 'int x = 1;',
      validation_status: 'proposed',
      related_diagnostics: [],
    };

    const res = await applyCorrection('int x = 1;', 'wrong_version', mockProposal);
    expect(res.success).toBe(false);
    expect(res.error_message).toContain('Stale proposal');
  });

  it('handles network failure with ApiError', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('Connection refused'));

    await expect(analyzeCode('int x = 1;')).rejects.toThrow(ApiError);
  });
});
