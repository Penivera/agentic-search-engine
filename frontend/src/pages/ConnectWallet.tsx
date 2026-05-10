import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import { useWallet } from "@solana/wallet-adapter-react";
import { useAuth } from "../context/AuthContext";
import { Bot, ArrowLeft, Loader2, AlertCircle } from "lucide-react";
import { Button } from "../components/ui/button";

export default function ConnectWallet() {
  const navigate = useNavigate();
  const location = useLocation();
  const { connected } = useWallet();
  const { authenticateWithWallet, isAuthenticated } = useAuth();
  
  const [error, setError] = useState("");
  const [isSigningIn, setIsSigningIn] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  // If already authenticated, redirect
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  // When a wallet connects, automatically start the SIWS flow
  useEffect(() => {
    if (connected && !isAuthenticated && !isSigningIn) {
      const signIn = async () => {
        setIsSigningIn(true);
        setError("");
        try {
          await authenticateWithWallet();
          navigate(from, { replace: true });
        } catch (err: any) {
          setError(err.message || "Failed to authenticate wallet");
        } finally {
          setIsSigningIn(false);
        }
      };
      
      signIn();
    }
  }, [connected, isAuthenticated, authenticateWithWallet, isSigningIn, navigate, from]);

  return (
    <main className="min-h-screen bg-background flex flex-col items-center justify-center p-4 relative">
      <div className="fixed top-4 left-4 z-50">
        <Button variant="ghost" size="sm" onClick={() => navigate("/")} className="gap-2">
          <ArrowLeft className="size-4" />
          <span className="hidden sm:inline">Back</span>
        </Button>
      </div>

      <div className="w-full max-w-md bg-surface/20 border border-border backdrop-blur-sm p-8 rounded-2xl shadow-xl flex flex-col items-center text-center">
        <div className="h-16 w-16 bg-primary/10 rounded-xl flex items-center justify-center mb-6">
          <Bot className="h-8 w-8 text-primary" />
        </div>
        
        <h1 className="text-3xl font-bold mb-2">Connect Wallet</h1>
        <p className="text-muted text-sm mb-8">
          Securely authenticate with your Solana wallet. No password required.
        </p>

        {error && (
          <div className="w-full mb-6 p-4 bg-destructive/10 border border-destructive/20 text-destructive text-sm rounded-lg flex items-center gap-3 text-left">
            <AlertCircle className="size-5 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {isSigningIn ? (
          <div className="flex flex-col items-center gap-4 w-full">
            <Loader2 className="size-8 animate-spin text-primary" />
            <p className="text-sm font-medium animate-pulse text-foreground/80">
              Please sign the message in your wallet...
            </p>
          </div>
        ) : (
          <div className="w-full flex justify-center solana-wallet-btn-container">
            <WalletMultiButton className="!bg-primary hover:!bg-primary/90 !transition-colors !rounded-lg !h-12 !px-8 !font-semibold !text-primary-foreground" />
          </div>
        )}
      </div>
      
      <p className="mt-8 text-sm text-muted">
        By connecting, you agree to our Terms of Service.
      </p>

      {/* Adding a global style to override the wallet adapter button to match our theme */}
      <style>{`
        .solana-wallet-btn-container .wallet-adapter-button {
          width: 100%;
          justify-content: center;
          font-family: inherit;
        }
      `}</style>
    </main>
  );
}
