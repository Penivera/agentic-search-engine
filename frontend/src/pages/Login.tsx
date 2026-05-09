import { useState } from "react"
import { useNavigate, Link, useSearchParams } from "react-router-dom"
import { Loader2, LogIn } from "lucide-react"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { ThemeToggle } from "../components/ThemeToggle"
import HomeBackground from "../components/HomeBg"
import { useAuth } from "../context/AuthContext"

export default function Login() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const redirect = searchParams.get("redirect") || "/home"
  const { login } = useAuth()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      await login(email, password)
      navigate(redirect)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-background text-foreground flex items-center justify-center px-4">
      <HomeBackground />

      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="h-120 w-120 rounded-full bg-primary/20 blur-[120px]" />
      </div>

      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-14 w-14 rounded-xl bg-primary/10 mb-4">
            <LogIn className="h-7 w-7 text-primary" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Welcome back</h1>
          <p className="text-muted-foreground mt-2">Sign in to your ASE account</p>
        </div>

        <form
          onSubmit={onSubmit}
          className="space-y-4 rounded-2xl border border-border/60 bg-card/65 p-6 backdrop-blur-xl shadow-lg shadow-primary/5"
        >
          <div className="grid gap-1.5">
            <label htmlFor="login-email" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Email
            </label>
            <Input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>

          <div className="grid gap-1.5">
            <label htmlFor="login-password" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Password
            </label>
            <Input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={8}
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/5 px-3 py-2">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <Button type="submit" disabled={submitting} className="w-full gap-2">
            {submitting ? <Loader2 className="size-4 animate-spin" /> : <LogIn className="size-4" />}
            {submitting ? "Signing in..." : "Sign In"}
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            Don't have an account?{" "}
            <Link
              to={`/signup${redirect !== "/home" ? `?redirect=${encodeURIComponent(redirect)}` : ""}`}
              className="font-medium text-primary hover:underline"
            >
              Sign up
            </Link>
          </p>
        </form>
      </div>
    </main>
  )
}
