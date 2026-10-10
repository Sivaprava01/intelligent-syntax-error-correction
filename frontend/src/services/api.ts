import type {
  AnalysisResponse,
  CorrectionResponse,
  ApplyProposalResponse,
  CorrectionProposal,
  HealthStatus,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  try {
    const response = await fetch(url, { ...options, headers });
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg =
        (data && data.detail) ||
        (data && data.error_message) ||
        `Request failed with status ${response.status}`;
      throw new ApiError(errorMsg, response.status, data);
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      error instanceof Error ? error.message : 'Network error or backend unreachable',
      0
    );
  }
}

export async function checkHealth(): Promise<HealthStatus> {
  return request<HealthStatus>('/api/health');
}

export async function analyzeCode(sourceCode: string): Promise<AnalysisResponse> {
  return request<AnalysisResponse>('/api/analyze', {
    method: 'POST',
    body: JSON.stringify({ source_code: sourceCode }),
  });
}

export async function requestCorrections(sourceCode: string): Promise<CorrectionResponse> {
  return request<CorrectionResponse>('/api/corrections', {
    method: 'POST',
    body: JSON.stringify({ source_code: sourceCode }),
  });
}

export async function applyCorrection(
  sourceCode: string,
  expectedSourceVersion: string,
  proposal: CorrectionProposal
): Promise<ApplyProposalResponse> {
  return request<ApplyProposalResponse>('/api/corrections/apply', {
    method: 'POST',
    body: JSON.stringify({
      source_code: sourceCode,
      expected_source_version: expectedSourceVersion,
      proposal,
    }),
  });
}
