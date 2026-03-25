import { useState, useEffect } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { Search, ArrowLeft, Loader2 } from "lucide-react"
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

  // Fetch results when query changes
  useEffect(() => {
    if (initialQuery.trim()) {
      fetchResults(initialQuery)
    } else {
      setResults([])
    }
  }, [initialQuery])

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
    snippet: result.skill.substring(0, 150) + (result.skill.length > 150 ? '...' : ''),
    skills: result.platform_description ? [result.platform_description] : [],
    relevanceScore: result.similarity,
    fileSource: result.skill_md_url ? 'SKILL.md' : 'API',
  }))

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">

      <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-4 h-20 flex items-center gap-4">

          <Button variant="ghost" size="icon" onClick={() => navigate("/")} className="shrink-0">
            <ArrowLeft className="size-5" />
          </Button>

          <form onSubmit={onSearch} className="relative flex-1 group max-w-2xl">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search agents..."
              className="h-11 pl-4 pr-12 rounded-xl bg-muted/20 border-border focus:ring-2 focus:ring-primary/20 transition-all"
            />
            <div className="absolute right-1 top-1/2 -translate-y-1/2">
              <Button type="submit" variant="ghost" size="icon" className="h-9 w-9" disabled={loading}>
                {loading ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
              </Button>
            </div>
          </form>

          <ThemeToggle />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-sm font-medium text-muted uppercase tracking-widest">
            Results for: <span className="text-foreground italic">"{initialQuery}"</span>
          </h2>
          <span className="text-xs text-muted">
            {loading ? 'Searching...' : `Found ${results.length} agents`}
          </span>
        </div>

        {loading && (
          <div className="text-center py-20">
            <Loader2 className="size-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted">Searching for matching skills...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-20 border-2 border-red-500/20 rounded-3xl bg-red-500/5">
            <p className="text-red-600 font-medium">Error: {error}</p>
            <p className="text-muted text-sm mt-2">Please try again or check the API connection</p>
          </div>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 gap-4">
            {cardResults.map((result) => (
              <SearchResultCard key={result.id} result={result} />
            ))}

            {results.length === 0 && initialQuery && (
              <div className="text-center py-20 border-2 border-dashed border-border rounded-3xl">
                <p className="text-muted">No agents found for that query.</p>
                <Button className="mt-4" variant="outline" onClick={() => navigate("/register")}>
                  Register a Product
                </Button>
              </div>
            )}

            {results.length === 0 && !initialQuery && (
              <div className="text-center py-20 border-2 border-dashed border-border rounded-3xl">
                <p className="text-muted">Enter a query to search for agents.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}