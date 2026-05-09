import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import {
  registerUser as apiRegister,
  loginUser as apiLogin,
  logoutUser as apiLogout,
  getMe,
  type AuthUser,
} from "../services/api";

// ─── Types ───────────────────────────────────────────────────

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

// ─── Constants ───────────────────────────────────────────────

const TOKEN_KEY = "ase_token";
const USER_KEY = "ase_user";

// ─── Context ─────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an <AuthProvider>");
  }
  return ctx;
}

// ─── Provider ────────────────────────────────────────────────

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Persist token + user to localStorage
  const persist = useCallback((token: string, user: AuthUser) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    setState({ user, token, isAuthenticated: true, isLoading: false });
  }, []);

  const clear = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setState({ user: null, token: null, isAuthenticated: false, isLoading: false });
  }, []);

  // On mount: rehydrate from localStorage and validate token
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (!storedToken || !storedUser) {
      setState((s) => ({ ...s, isLoading: false }));
      return;
    }

    // Validate with backend
    getMe(storedToken)
      .then((user) => {
        persist(storedToken, user);
      })
      .catch(() => {
        clear();
      });
  }, [persist, clear]);

  // ─── Actions ─────────────────────────────────────────────

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await apiLogin(email, password);
      if (!res.access_token || !res.user) {
        throw new Error(res.message || "Login failed");
      }
      persist(res.access_token, res.user);
    },
    [persist],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const res = await apiRegister(email, password);
      if (res.verification_required) {
        throw new Error("Email verification required. Please check your email.");
      }
      if (!res.access_token || !res.user) {
        throw new Error(res.message || "Registration failed");
      }
      persist(res.access_token, res.user);
    },
    [persist],
  );

  const logout = useCallback(async () => {
    if (state.token) {
      try {
        await apiLogout(state.token);
      } catch {
        // Logout on backend failed — still clear locally
      }
    }
    clear();
  }, [state.token, clear]);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
