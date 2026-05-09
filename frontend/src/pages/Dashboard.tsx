import { useState, useEffect, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowLeft, Loader2, Plus, Trash2, ExternalLink, Globe } from "lucide-react"
import { Button } from "../components/ui/button"
import { ThemeToggle } from "../components/ThemeToggle"
import HomeBackground from "../components/HomeBg"
import { useAuth } from "../context/AuthContext"
import { listPlatforms, deletePlatform, type PlatformItem } from "../services/api"

export default function Dashboard() {
  const navigate = useNavigate()
  const { isAuthenticated, isLoading: authLoading, token, user, logout } = useAuth()

  const [platforms, setPlatforms] = useState<PlatformItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate("/login?redirect=/dashboard")
    }
  }, [authLoading, isAuthenticated, navigate])

  const fetchPlatforms = useCallback(async () => {
    if (!token || !user) return
    setLoading(true)
    setError(null)

    try {
      const all = await listPlatforms()
      // Filter to user's own platforms
      const mine = all.filter((p) => p.owner_id === user.id)
      setPlatforms(mine)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load platforms")
    } finally {
      setLoading(false)
    }
  }, [token, user])

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchPlatforms()
    }
  }, [isAuthenticated, token, fetchPlatforms])

  const handleDelete = async (id: string) => {
    if (!token) return
    setDeletingId(id)
    try {
      await deletePlatform(id, token)
      setPlatforms((prev) => prev.filter((p) => p.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete platform")
    } finally {
      setDeletingId(null)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate("/")
  }

  if (authLoading) {
    return (
      <main className="relative min-h-screen overflow-hidden bg-background text-foreground flex items-center justify-center">
        <Loader2 className="size-8 animate-spin text-primary" />
      </main>
    )
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-background text-foreground px-4 py-8">
      <HomeBackground />

      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="h-120 w-120 rounded-full bg-primary/20 blur-[120px]" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button variant="ghost" size="sm" onClick={() => navigate("/home")} className="gap-2">
            <ArrowLeft className="size-4" /> Back
          </Button>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden sm:inline">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              Sign Out
            </Button>
            <ThemeToggle />
          </div>
        </div>

        {/* Title area */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground mt-1">Manage your registered platforms</p>
          </div>
          <Button onClick={() => navigate("/register")} className="gap-2">
            <Plus className="size-4" /> Register Product
          </Button>
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/5 px-4 py-3 mb-6">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="text-center py-20">
            <Loader2 className="size-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading your platforms...</p>
          </div>
        )}

        {/* Empty state */}
        {!loading && platforms.length === 0 && (
          <div className="text-center py-20 rounded-2xl border-2 border-dashed border-border bg-card/30 backdrop-blur-sm">
            <Globe className="size-12 mx-auto mb-4 text-muted-foreground/50" />
            <h2 className="text-lg font-semibold mb-2">No platforms yet</h2>
            <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
              Register your first agentic product to start getting discovered in search.
            </p>
            <Button onClick={() => navigate("/register")} className="gap-2">
              <Plus className="size-4" /> Register Your First Product
            </Button>
          </div>
        )}

        {/* Platform list */}
        {!loading && platforms.length > 0 && (
          <div className="space-y-4">
            {platforms.map((platform) => (
              <div
                key={platform.id}
                className="group rounded-xl border border-border/60 bg-card/65 p-5 backdrop-blur-xl shadow-sm hover:shadow-md hover:border-primary/30 transition-all"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <h3 className="text-lg font-semibold truncate">{platform.name}</h3>
                    {platform.description && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{platform.description}</p>
                    )}

                    <div className="flex flex-wrap items-center gap-3 mt-3 text-xs text-muted-foreground">
                      <a
                        href={platform.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 hover:text-primary transition-colors"
                      >
                        <ExternalLink className="size-3" />
                        {new URL(platform.url).hostname}
                      </a>

                      {platform.skills_url && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 text-primary px-2 py-0.5 font-medium">
                          SKILL.md
                        </span>
                      )}

                      {platform.created_at && (
                        <span>
                          Added {new Date(platform.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="icon"
                    className="shrink-0 text-muted-foreground hover:text-red-500 hover:bg-red-500/10"
                    disabled={deletingId === platform.id}
                    onClick={() => handleDelete(platform.id)}
                  >
                    {deletingId === platform.id ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Trash2 className="size-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}