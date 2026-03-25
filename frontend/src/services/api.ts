import API_URL from '../lib/api';

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
  skills_url: string;
}

// Search for skills
export async function searchSkills(query: string, topK: number = 5): Promise<SearchResult[]> {
  try {
    const params = new URLSearchParams({
      query,
      top_k: topK.toString(),
    });
    
    const response = await fetch(`${API_URL}/search?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to search skills: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Search error:', error);
    throw error;
  }
}

// Register a skill
export async function registerSkill(skill: SkillPayload, token?: string): Promise<any> {
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/skills`, {
      method: 'POST',
      headers,
      body: JSON.stringify(skill),
    });

    if (!response.ok) {
      throw new Error(`Failed to register skill: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

// Get full skill details
export async function getSkillDetails(platformId: string): Promise<any> {
  try {
    const response = await fetch(`${API_URL}/skills/by-platform/${platformId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch skill details: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}

// Register a platform
export async function registerPlatform(platform: PlatformPayload, token?: string): Promise<any> {
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/platforms/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(platform),
    });

    if (!response.ok) {
      throw new Error(`Failed to register platform: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Platform registration error:', error);
    throw error;
  }
}

// List all platforms
export async function listPlatforms(): Promise<any[]> {
  try {
    const response = await fetch(`${API_URL}/platforms`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to list platforms: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('List platforms error:', error);
    throw error;
  }
}
