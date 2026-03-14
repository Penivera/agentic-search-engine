import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Search } from "lucide-react"
import { Input } from "../../src/components/ui/input"
import { Button } from "../components/ui/button"
import { ThemeToggle } from "../components/ThemeToggle" 
import HomeBackground from "../components/HomeBg"
import { Terminal } from "lucide-react"

export default function Home() {
  const [query, setQuery] = useState("")
  const navigate = useNavigate()

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}`)
    }
  }

  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center p-6 overflow-hidden bg-background text-foreground transition-colors duration-300">
        <HomeBackground />


      <div className="fixed top-4 left-4 z-50">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => navigate("/console")}
          className="gap-2 hover:text-primary hover:bg-primary/5 transition-all"
        >
          <Terminal className="size-4" />
          <span className="hidden sm:inline font-semibold uppercase tracking-wider text-[12px]">
            Search Console
          </span>
        </Button>
      </div>

      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="h-150 w-150 rounded-full bg-primary/20 blur-[120px]" />
      </div>

      <div className="relative z-10 w-full max-w-4xl text-center mb-25">
        <h1 className="text-5xl font-bold tracking-tight md:text-7xl mb-2">
          Agentic <span className="text-primary">Search</span>
        </h1>
        <p className="text-muted mb-10 md:text-lg">
          Find skills, tools, and agents instantly.
        </p>

        <form onSubmit={onSearch} className="relative group max-w-3xl mx-auto w-full">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for agent skills..."
            className="h-16 pl-6 pr-14 rounded-2xl border-border bg-background/50 backdrop-blur-md shadow-xl transition-all focus:ring-4 focus:ring-primary/10"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <Button 
              type="submit"
              size="icon" 
              variant="ghost" 
              className="h-10 w-10"
            >
              <Search className="size-6" />
              <span className="sr-only">Search</span>
            </Button>
          </div>
        </form>
      </div>
    </main>
  )
}