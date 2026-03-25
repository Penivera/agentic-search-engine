import { useNavigate } from "react-router-dom"
import { Copy, Check, Bot, ArrowLeft } from "lucide-react"
import { useState } from "react"
import { Button } from "../components/ui/button"
import { ThemeToggle } from "../components/ThemeToggle"

export default function AgentPage() {
  const navigate = useNavigate()
  const [copied, setCopied] = useState(false)

  const backendBaseUrl = "https://ase-f1e2b8fd.fastapicloud.dev"
  const skillCommand = `curl -sS ${backendBaseUrl}/skill.md`
  const skillmdContent = `# Agentic Search Engine Skill
\`\`\`yaml
name: agentic-search-engine
type: skill
version: 1.0.0
description: Semantic search engine for discovering and indexing agent skills
endpoints:
  - GET /api/search?query=...&top_k=5
  - POST /api/skills
  - GET /api/platforms
author: Penivera
\`\`\``

  const handleCopy = () => {
    navigator.clipboard.writeText(skillCommand)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <main className="min-h-screen bg-background text-foreground transition-colors duration-300">
      <div className="fixed top-4 left-4 z-50">
        <Button variant="ghost" size="sm" onClick={() => navigate("/")} className="gap-2">
          <ArrowLeft className="size-4" />
          <span className="hidden sm:inline">Back</span>
        </Button>
      </div>

      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      <div className="max-w-4xl mx-auto px-6 py-20">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <div className="h-16 w-16 rounded-lg bg-primary/10 flex items-center justify-center">
              <Bot className="h-8 w-8 text-primary" />
            </div>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Agent Integration
          </h1>
          <p className="text-muted text-lg max-w-2xl mx-auto">
            Get the SKILL.md file to integrate Agentic Search Engine capabilities into your agent.
          </p>
        </div>

        {/* Command Section */}
        <div id="skill-file" className="mb-12 scroll-mt-24">
          <h2 className="text-xl font-semibold mb-4">Integration Command</h2>
          
          <div className="relative group rounded-lg border border-border/50 bg-muted/20 p-6 backdrop-blur-sm">
            <code className="text-sm font-mono text-foreground/80 break-all">
              {skillCommand}
            </code>
            
            <Button
              onClick={handleCopy}
              size="sm"
              variant="outline"
              className="absolute top-4 right-4 gap-2"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Copy
                </>
              )}
            </Button>
          </div>
        </div>

        {/* SKILL.md Preview */}
        <div className="mb-12">
          <h2 className="text-xl font-semibold mb-4">SKILL.md Preview</h2>
          
          <div className="rounded-lg border border-border/50 bg-muted/20 p-6 backdrop-blur-sm overflow-x-auto">
            <pre className="text-sm font-mono text-foreground/80 whitespace-pre-wrap break-words">
              {skillmdContent}
            </pre>
          </div>
        </div>

        {/* API Endpoints */}
        <div className="mb-12">
          <h2 className="text-xl font-semibold mb-4">Available Endpoints</h2>
          
          <div className="space-y-4">
            <div className="rounded-lg border border-border/50 bg-card/50 p-4 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="rounded px-3 py-1 bg-blue-500/10 text-blue-600 font-mono text-xs font-bold">
                  GET
                </div>
                <div className="flex-1">
                  <code className="text-sm font-mono">/api/search</code>
                  <p className="text-xs text-muted mt-1">
                    Search skills by query. Full URL: {backendBaseUrl}/api/search
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-border/50 bg-card/50 p-4 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="rounded px-3 py-1 bg-green-500/10 text-green-600 font-mono text-xs font-bold">
                  POST
                </div>
                <div className="flex-1">
                  <code className="text-sm font-mono">/api/skills</code>
                  <p className="text-xs text-muted mt-1">
                    Register a new skill. Full URL: {backendBaseUrl}/api/skills
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-border/50 bg-card/50 p-4 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="rounded px-3 py-1 bg-purple-500/10 text-purple-600 font-mono text-xs font-bold">
                  GET
                </div>
                <div className="flex-1">
                  <code className="text-sm font-mono">/api/platforms</code>
                  <p className="text-xs text-muted mt-1">
                    List available platforms. Full URL: {backendBaseUrl}/api/platforms
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="rounded-lg border border-border/50 bg-card/50 p-6 backdrop-blur-sm">
          <h2 className="text-xl font-semibold mb-4">Next Steps</h2>
          
          <ol className="space-y-3 text-sm">
            <li className="flex gap-3">
              <span className="flex-shrink-0 h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold">
                1
              </span>
              <span>Copy the integration command above</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold">
                2
              </span>
              <span>Integrate with your agent/LLM system</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold">
                3
              </span>
              <span>Use {backendBaseUrl}/api/search for discovery</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold">
                4
              </span>
              <span>Use {backendBaseUrl}/api/skills to register new skills</span>
            </li>
          </ol>
        </div>
      </div>
    </main>
  )
}
