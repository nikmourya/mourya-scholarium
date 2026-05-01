/**
 * Mourya Scholarium — Zustand Store
 * Global state: auth, profile, projects, writing sessions
 */
import { create } from 'zustand';

// Use empty string for relative URLs in dev (leverages Next.js proxy rewrite).
// In production, set NEXT_PUBLIC_API_URL to the deployed backend URL.
const API = process.env.NEXT_PUBLIC_API_URL ?? '';

interface UserProfile {
  english_level: string;
  academic_level: string;
  discipline: string;
  citation_style: string;
  target_output_level: string;
  preservation_priorities: string[];
  improvement_targets: string[];
}

interface WritingResult {
  session_id: string;
  text: string;
  word_count: number;
  sources: any[];
  bibliography: string[];
  evidence_traces: any[];
  integrity_status: string;
  integrity_report: any;
}

interface AppState {
  // Auth
  token: string | null;
  user: { id: string; name: string; email: string } | null;
  // Profile
  profile: UserProfile | null;
  styleSignature: any | null;
  // Projects
  projects: any[];
  // Writing
  currentResult: WritingResult | null;
  isGenerating: boolean;
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string, institution?: string) => Promise<void>;
  logout: () => void;
  saveProfile: (profile: UserProfile) => Promise<void>;
  uploadStyleSample: (text: string) => Promise<any>;
  loadProjects: () => Promise<void>;
  createProject: (title: string, projectType?: string) => Promise<void>;
  submitWriteRequest: (req: any) => Promise<void>;
  submitFeedback: (sessionId: string, signalType: string) => Promise<void>;
}

/**
 * Helper: make a fetch call with structured error handling.
 * Returns the Response on success, throws a user-friendly Error on failure.
 */
async function apiFetch(path: string, options?: RequestInit): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(`${API}${path}`, options);
  } catch (networkError) {
    // fetch() itself threw — network-level failure (server unreachable, DNS, etc.)
    throw new Error(
      'Cannot connect to the server. Please make sure the backend is running on ' +
      (API || 'http://localhost:8000') + ' and try again.'
    );
  }

  if (!res.ok) {
    // Server responded with an error status
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
    } catch {
      // Response wasn't JSON — use status text
      detail = res.statusText || detail;
    }
    throw new Error(detail);
  }

  return res;
}

const useStore = create<AppState>((set, get) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('ms_token') : null,
  user: typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('ms_user') || 'null') : null,
  profile: null,
  styleSignature: null,
  projects: [],
  currentResult: null,
  isGenerating: false,

  login: async (email, password) => {
    const res = await apiFetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    localStorage.setItem('ms_token', data.token);
    localStorage.setItem('ms_user', JSON.stringify({ id: data.user_id, name: data.name, email: data.email }));
    set({ token: data.token, user: { id: data.user_id, name: data.name, email: data.email } });
  },

  register: async (email, name, password, institution) => {
    const res = await apiFetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name, password, institution: institution || null }),
    });
    const data = await res.json();
    localStorage.setItem('ms_token', data.token);
    localStorage.setItem('ms_user', JSON.stringify({ id: data.user_id, name: data.name, email: data.email }));
    set({ token: data.token, user: { id: data.user_id, name: data.name, email: data.email } });
  },

  logout: () => {
    localStorage.removeItem('ms_token');
    localStorage.removeItem('ms_user');
    set({ token: null, user: null, profile: null, projects: [], currentResult: null });
  },

  saveProfile: async (profile) => {
    const { token } = get();
    await apiFetch('/api/v1/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(profile),
    });
    set({ profile });
  },

  uploadStyleSample: async (text) => {
    const { token } = get();
    const res = await apiFetch('/api/v1/profile/style-sample', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ sample_text: text }),
    });
    const data = await res.json();
    set({ styleSignature: data.features });
    return data;
  },

  loadProjects: async () => {
    const { token } = get();
    const res = await apiFetch('/api/v1/projects', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    set({ projects: data.projects || [] });
  },

  createProject: async (title, projectType) => {
    const { token } = get();
    await apiFetch('/api/v1/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title, project_type: projectType }),
    });
    get().loadProjects();
  },

  submitWriteRequest: async (req) => {
    const { token } = get();
    set({ isGenerating: true, currentResult: null });
    try {
      const res = await apiFetch('/api/v1/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(req),
      });
      const data = await res.json();
      set({
        currentResult: {
          session_id: data.session_id,
          text: data.output?.text || '',
          word_count: data.output?.word_count || 0,
          sources: data.sources || [],
          bibliography: data.bibliography || [],
          evidence_traces: data.evidence_traces || [],
          integrity_status: data.output?.integrity_status || 'unknown',
          integrity_report: data.integrity_report || {},
        },
      });
    } finally {
      set({ isGenerating: false });
    }
  },

  submitFeedback: async (sessionId, signalType) => {
    const { token } = get();
    await apiFetch(`/api/v1/write/${sessionId}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ signal_type: signalType }),
    });
  },
}));

export default useStore;
