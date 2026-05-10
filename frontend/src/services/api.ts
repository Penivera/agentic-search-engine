import API_URL from '../lib/api';

// ─── Types ───────────────────────────────────────────────────

export interface SearchResult {
  platform_name: string;
  platform_description?: string;
  platform_id: string;
  skill: string;
  similarity: number;
  skill_md_url?: string;
}

export interface SkillPayload {
  platform_id: string;
  skill_name?: string;
  tags?: string[];
  capabilities: string;
}

export interface PlatformPayload {
  name: string;
  url: string;
  homepage_uri: string;
  description?: string;
  skills_url?: string;
}

export interface AuthUser {
  id: string;
  wallet_address: string;
}

export interface AuthResponse {
  message: string;
  access_token?: string;
  token_type?: string;
  expires_at?: string;
  user?: AuthUser;
}

export interface NonceResponse {
  nonce: string;
}

export interface PlatformItem {
  id: string;
  name: string;
  url: string;
  homepage_uri: string;
  skills_url?: string;
  description?: string;
  owner_id?: string;
  created_at?: string;
}

// ─── Helpers ─────────────────────────────────────────────────

function authHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // use statusText
    }
    throw new Error(detail);
  }
  return response.json();
}

// ─── Auth ────────────────────────────────────────────────────

export async function getNonce(walletAddress: string): Promise<NonceResponse> {
  const response = await fetch(`${API_URL}/auth/nonce?wallet_address=${encodeURIComponent(walletAddress)}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });
  return handleResponse<NonceResponse>(response);
}

export async function verifyWallet(walletAddress: string, signature: string, nonce: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/auth/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: walletAddress, signature, nonce }),
  });
  return handleResponse<AuthResponse>(response);
}

export async function logoutUser(token: string): Promise<{ message: string }> {
  const response = await fetch(`${API_URL}/auth/logout`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse<{ message: string }>(response);
}

export async function getMe(token: string): Promise<AuthUser> {
  const response = await fetch(`${API_URL}/auth/me`, {
    method: 'GET',
    headers: authHeaders(token),
  });
  return handleResponse<AuthUser>(response);
}

// ─── Search ──────────────────────────────────────────────────

export async function searchSkills(query: string, topK: number = 5): Promise<SearchResult[]> {
  const params = new URLSearchParams({
    query,
    top_k: topK.toString(),
  });

  const response = await fetch(`${API_URL}/search?${params}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });
  return handleResponse<SearchResult[]>(response);
}

// ─── Skills ──────────────────────────────────────────────────

export async function registerSkill(skill: SkillPayload, token?: string): Promise<any> {
  const response = await fetch(`${API_URL}/skills`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(skill),
  });
  return handleResponse(response);
}

export async function getSkillDetails(platformId: string): Promise<any> {
  const response = await fetch(`${API_URL}/skills/by-platform/${platformId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });
  return handleResponse(response);
}

// ─── Platforms ───────────────────────────────────────────────

export async function registerPlatform(platform: PlatformPayload, token?: string): Promise<any> {
  const response = await fetch(`${API_URL}/platforms/`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(platform),
  });
  return handleResponse(response);
}

export async function listPlatforms(): Promise<PlatformItem[]> {
  const response = await fetch(`${API_URL}/platforms`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });
  return handleResponse<PlatformItem[]>(response);
}

export async function deletePlatform(platformId: string, token: string): Promise<{ message: string; id: string }> {
  const response = await fetch(`${API_URL}/platforms/${platformId}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  return handleResponse<{ message: string; id: string }>(response);
}
