import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { useWallet } from "@solana/wallet-adapter-react";
import bs58 from "bs58";
import {
  getNonce,
  verifyWallet,
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
  authenticateWithWallet: () => Promise<void>;
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
  const { publicKey, signMessage, disconnect, connected } = useWallet();

  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const persist = useCallback((token: string, user: AuthUser) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    setState({ user, token, isAuthenticated: true, isLoading: false });
  }, []);

  const clear = useCallback(async () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setState({ user: null, token: null, isAuthenticated: false, isLoading: false });
    if (connected) {
      try {
        await disconnect();
      } catch {
        // Ignore disconnect errors
      }
    }
  }, [connected, disconnect]);

  // On mount: rehydrate from localStorage and validate token
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (!storedToken || !storedUser) {
      setState((s) => ({ ...s, isLoading: false }));
      return;
    }

    getMe(storedToken)
      .then((user) => {
        persist(storedToken, user);
      })
      .catch(() => {
        clear();
      });
  }, [persist, clear]);

  // ─── Actions ─────────────────────────────────────────────

  const authenticateWithWallet = useCallback(async () => {
    if (!publicKey || !signMessage) {
      throw new Error("Wallet not connected or does not support message signing");
    }

    const walletAddress = publicKey.toBase58();

    // 1. Fetch nonce
    const { nonce } = await getNonce(walletAddress);

    // 2. Sign message
    const message = `Sign this message to authenticate with ASE. Nonce: ${nonce}`;
    const messageBytes = new TextEncoder().encode(message);
    
    const signatureBytes = await signMessage(messageBytes);
    const signature = bs58.encode(signatureBytes);

    // 3. Verify on backend
    const res = await verifyWallet(walletAddress, signature, nonce);
    
    if (!res.access_token || !res.user) {
      throw new Error(res.message || "Authentication failed");
    }

    // 4. Persist
    persist(res.access_token, res.user);
  }, [publicKey, signMessage, persist]);

  const logout = useCallback(async () => {
    if (state.token) {
      try {
        await apiLogout(state.token);
      } catch {
        // Logout on backend failed — still clear locally
      }
    }
    await clear();
  }, [state.token, clear]);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        authenticateWithWallet,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
