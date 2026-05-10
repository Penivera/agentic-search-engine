import { useState, useEffect } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { Search, ArrowLeft, Loader2, Filter, Zap } from "lucide-react"
import { Input } from "../../src/components/ui/input"
import { Button } from "../../src/components/ui/button"
import { ThemeToggle } from "../../src/components/ThemeToggle"
import { SearchResultCard } from "../../src/components/results"
import type { SearchResult } from "../services/api"
import { searchSkills } from "../services/api"

export default function SearchResults() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const initialQuery = searchParams.get("q") || ""
  
  const [query, setQuery] = useState(initialQuery)
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Animation state
  const [visibleItems, setVisibleItems] = useState<number>(0)

  // Fetch results when query changes
  useEffect(() => {
    if (initialQuery.trim()) {
      fetchResults(initialQuery)
    } else {
      setResults([])
    }
  }, [initialQuery])

  // Stagger animation effect
  useEffect(() => {
    if (!loading && results.length > 0) {
      setVisibleItems(0)
      const timer = setInterval(() => {
        setVisibleItems((prev) => {
          if (prev >= results.length) {
            clearInterval(timer)
            return prev
          }
          return prev + 1
        })
      }, 100)
      return () => clearInterval(timer)
    }
  }, [loading, results])

  const fetchResults = async (searchQuery: string) => {
    if (!searchQuery.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      const data = await searchSkills(searchQuery, 10)
      setResults(data)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch results'
      setError(errorMessage)
      console.error('Search error:', err)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}`)
    }
  }

  // Convert API response to card format
  const cardResults = results.map((result) => ({
    id: result.platform_id,
    title: result.platform_name,
    snippet: result.skill,
    skills: result.tags || (result.platform_description ? [result.platform_description.substring(0, 20)] : []),
    relevanceScore: result.similarity,
    fileSource: result.skill_md_url ? 'SKILL.md' : 'Direct API',
    url: result.platform_url
  }))

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl shadow-sm">
        <div className="max-w-6xl mx-auto px-4 h-20 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate("/home")} className="shrink-0 hover:bg-muted/50 rounded-full">
            <ArrowLeft className="size-5" />
          </Button>

          <form onSubmit={onSearch} className="relative flex-1 group max-w-2xl mx-auto">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search agents, tools, skills..."
              className="h-12 pl-5 pr-12 rounded-full bg-muted/30 border-border/60 focus:ring-2 focus:ring-primary/20 focus:border-primary/50 transition-all shadow-sm"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2">
              <Button type="submit" variant="ghost" size="icon" className="h-8 w-8 rounded-full" disabled={loading}>
                {loading ? <Loader2 className="size-4 animate-spin text-primary" /> : <Search className="size-4 text-muted-foreground" />}
              </Button>
            </div>
          </form>

          <ThemeToggle />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Filters & Meta */}
        <div className="mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-border/40 pb-4">
          <div>
            <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-widest flex items-center gap-2">
              <Search className="size-3" />
              Results for: <span className="text-foreground italic normal-case font-semibold">"{initialQuery}"</span>
            </h2>
            <p className="text-xs text-muted-foreground mt-1">
              {loading ? 'Analyzing semantic space...' : `Found ${results.length} highly relevant agents`}
            </p>
          </div>
          
          {!loading && results.length > 0 && (
            <div className="flex gap-2">
              <BadgeFilter active>All</BadgeFilter>
              <BadgeFilter>Verified</BadgeFilter>
              <BadgeFilter>Fast Response</BadgeFilter>
            </div>
          )}
        </div>

        {loading && (
          <div className="text-center py-32 flex flex-col items-center justify-center">
            <div className="relative">
              <div className="absolute inset-0 rounded-full blur-xl bg-primary/20 animate-pulse" />
              <Loader2 className="size-10 animate-spin text-primary relative z-10" />
            </div>
            <p className="text-muted-foreground font-medium mt-6 animate-pulse">Running semantic search...</p>
            <p className="text-xs text-muted mt-2">Matching query intent against agent capabilities</p>
          </div>
        )}

        {error && (
          <div className="text-center py-20 border border-destructive/20 rounded-3xl bg-destructive/5 backdrop-blur-sm shadow-sm">
            <div className="size-12 rounded-full bg-destructive/10 text-destructive flex items-center justify-center mx-auto mb-4">
              <Zap className="size-6" />
            </div>
            <p className="text-destructive font-semibold">Error: {error}</p>
            <p className="text-muted-foreground text-sm mt-2">Our AI encountered an issue processing the request.</p>
            <Button className="mt-6" variant="outline" onClick={() => fetchResults(initialQuery)}>
              Try Again
            </Button>
          </div>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 gap-5">
            {cardResults.map((result, idx) => (
              <div 
                key={result.id} 
                className={`transition-all duration-500 ease-out ${
                  idx < visibleItems 
                    ? "opacity-100 translate-y-0" 
                    : "opacity-0 translate-y-8"
                }`}
              >
                <SearchResultCard result={result} />
              </div>
            ))}

            {results.length === 0 && initialQuery && (
              <div className="text-center py-32 border-2 border-dashed border-border/60 rounded-3xl bg-muted/5">
                <div className="size-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                  <Filter className="size-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">No agents found</h3>
                <p className="text-muted-foreground max-w-md mx-auto">
                  We couldn't find any agent skills matching "{initialQuery}". Try adjusting your semantic search terms.
                </p>
                <Button className="mt-8 gap-2" variant="default" onClick={() => navigate("/register")}>
                  Register a Product
                </Button>
              </div>
            )}

            {results.length === 0 && !initialQuery && (
              <div className="text-center py-32 border border-border/50 rounded-3xl bg-card/30 backdrop-blur-sm shadow-sm">
                <h3 className="text-xl font-medium text-foreground mb-2">Ready to search</h3>
                <p className="text-muted-foreground">Enter a capability or tool you need above.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

function BadgeFilter({ children, active }: { children: React.ReactNode, active?: boolean }) {
  return (
    <button className={`px-3 py-1 text-xs rounded-full border transition-colors ${
      active 
        ? "bg-primary text-primary-foreground border-primary" 
        : "bg-background text-muted-foreground border-border hover:border-primary/50"
    }`}>
      {children}
    </button>
  )
}