import { useState } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { Search, ArrowLeft } from "lucide-react"
import { Input } from "../../src/components/ui/input"
import { Button } from "../../src/components/ui/button"
import { ThemeToggle } from "../../src/components/ThemeToggle"
import { SearchResultCard } from "../../src/components/results"
import { mockResults } from "../data/searchData"

export default function SearchResults() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const initialQuery = searchParams.get("q") || ""
  
  const [query, setQuery] = useState(initialQuery)

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}`)
    }
  }

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
              <Button type="submit" variant="ghost" size="icon" className="h-9 w-9">
                <Search className="size-4" />
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
          <span className="text-xs text-muted">Found {mockResults.length} agents</span>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {mockResults.map((result) => (
            <SearchResultCard key={result.id} result={result} />
          ))}

          {mockResults.length === 0 && (
            <div className="text-center py-20 border-2 border-dashed border-border rounded-3xl">
              <p className="text-muted">No agents found for that query.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}