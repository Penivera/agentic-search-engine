import { useNavigate } from "react-router-dom"
import { Bot, Users, ChevronRight } from "lucide-react"
import { Button } from "../components/ui/button"
import { ThemeToggle } from "../components/ThemeToggle"
import HomeBackground from "../components/HomeBg"

export default function Landing() {
  const navigate = useNavigate()

  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center p-6 overflow-hidden bg-background text-foreground transition-colors duration-300">
      <HomeBackground />

      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="h-150 w-150 rounded-full bg-primary/20 blur-[120px]" />
      </div>

      <div className="relative z-10 w-full max-w-4xl">
        <div className="text-center mb-20">
          <h1 className="text-5xl font-bold tracking-tight md:text-7xl mb-4">
            ASE <span className="text-primary">(Agentic Search Engine)</span>
          </h1>
          <p className="text-muted md:text-lg">
            Discover and integrate agent skills effortlessly.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-2xl mx-auto">
          {/* Agent Option */}
          <div
            onClick={() => navigate("/agent")}
            className="group relative overflow-hidden rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8 cursor-pointer transition-all hover:border-primary/50 hover:bg-card/80 hover:shadow-lg hover:shadow-primary/10"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-6">
                <div className="h-14 w-14 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <Bot className="h-7 w-7 text-primary" />
                </div>
                <ChevronRight className="h-5 w-5 text-muted group-hover:text-primary transition-colors" />
              </div>

              <h2 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">
                I'm an Agent
              </h2>
              <p className="text-muted text-sm leading-relaxed mb-4">
                Access integration commands and retrieve skill definitions.
              </p>

              <div className="grid gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full group-hover:bg-primary/10 group-hover:border-primary/50 transition-all"
                >
                  Open Agent Section
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="w-full"
                  onClick={(event) => {
                    event.stopPropagation()
                    navigate("/agent#skill-file")
                  }}
                >
                  Go To SKILL.md Command
                </Button>
              </div>
            </div>
          </div>

          {/* Human Option */}
          <div
            onClick={() => navigate("/home")}
            className="group relative overflow-hidden rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8 cursor-pointer transition-all hover:border-primary/50 hover:bg-card/80 hover:shadow-lg hover:shadow-primary/10"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-6">
                <div className="h-14 w-14 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <Users className="h-7 w-7 text-primary" />
                </div>
                <ChevronRight className="h-5 w-5 text-muted group-hover:text-primary transition-colors" />
              </div>

              <h2 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">
                I'm a Human
              </h2>
              <p className="text-muted text-sm leading-relaxed mb-4">
                Search for skills, explore agents, and discover integrations.
              </p>
              
              <Button
                size="sm"
                variant="outline"
                className="w-full group-hover:bg-primary/10 group-hover:border-primary/50 transition-all"
              >
                Search Skills
              </Button>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
