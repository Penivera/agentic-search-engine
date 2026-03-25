import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowLeft, Loader2 } from "lucide-react"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { ThemeToggle } from "../components/ThemeToggle"
import HomeBackground from "../components/HomeBg"
import { registerPlatform, registerSkill } from "../services/api"

export default function RegisterProduct() {
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [name, setName] = useState("")
  const [url, setUrl] = useState("")
  const [homepageUri, setHomepageUri] = useState("")
  const [description, setDescription] = useState("")
  const [skillsUrl, setSkillsUrl] = useState("")
  const [capabilities, setCapabilities] = useState("")
  const [skillName, setSkillName] = useState("")
  const [tags, setTags] = useState("")
  const [token, setToken] = useState("")

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    setSuccess(null)

    try {
      const platform = await registerPlatform(
        {
          name,
          url,
          homepage_uri: homepageUri,
          description: description || undefined,
          skills_url: skillsUrl,
        },
        token || undefined,
      )

      // Optional direct skill registration for immediate searchability.
      if (capabilities.trim()) {
        await registerSkill(
          {
            platform_id: platform.id,
            capabilities,
            skill_name: skillName || undefined,
            tags: tags
              ? tags
                  .split(",")
                  .map((t) => t.trim())
                  .filter(Boolean)
              : undefined,
          },
          token || undefined,
        )
      }

      setSuccess("Product registered successfully. It is now available for search.")
      const q = encodeURIComponent(skillName || name)
      setTimeout(() => navigate(`/search?q=${q}`), 900)
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Registration failed"
      setError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-background text-foreground px-4 py-8">
      <HomeBackground />

      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="h-120 w-120 rounded-full bg-primary/20 blur-[120px]" />
      </div>

      <div className="relative z-10 max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <Button variant="ghost" size="sm" onClick={() => navigate("/home")} className="gap-2">
            <ArrowLeft className="size-4" /> Back
          </Button>
          <ThemeToggle />
        </div>

        <h1 className="text-4xl font-bold tracking-tight mb-2">Register Agentic Product</h1>
        <p className="text-muted-foreground mb-8 max-w-2xl">
          Add your product so humans can discover it in semantic search.
        </p>

        <form onSubmit={onSubmit} className="space-y-5 rounded-2xl border border-border/60 bg-card/65 p-6 backdrop-blur-xl shadow-lg shadow-primary/5">
          <div className="grid gap-1">
            <label htmlFor="product-name" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Product Name
            </label>
            <Input id="product-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Product name" required />
          </div>

          <div className="grid gap-1">
            <label htmlFor="product-url" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Product URL
            </label>
            <Input id="product-url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://..." required />
          </div>

          <div className="grid gap-1">
            <label htmlFor="homepage-url" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Homepage URL
            </label>
            <Input
              id="homepage-url"
              value={homepageUri}
              onChange={(e) => setHomepageUri(e.target.value)}
              placeholder="https://..."
              required
            />
          </div>

          <div className="grid gap-1">
            <label htmlFor="product-description" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Description
            </label>
            <Input
              id="product-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Short description"
            />
          </div>

          <div className="grid gap-1">
            <label htmlFor="skill-file" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              SKILL.md URL
            </label>
            <Input
              id="skill-file"
              value={skillsUrl}
              onChange={(e) => setSkillsUrl(e.target.value)}
              placeholder="https://.../SKILL.md"
              required
            />
          </div>

          <div className="pt-2 border-t border-border/60" />

          <div className="grid gap-1">
            <label htmlFor="primary-skill" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Primary Skill Name
            </label>
            <Input
              id="primary-skill"
              value={skillName}
              onChange={(e) => setSkillName(e.target.value)}
              placeholder="Optional"
            />
          </div>

          <div className="grid gap-1">
            <label htmlFor="tags" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Tags
            </label>
            <Input
              id="tags"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="search, wallet, automation"
            />
          </div>

          <div className="grid gap-1">
            <label htmlFor="capabilities" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Capabilities
            </label>
            <textarea
              id="capabilities"
              value={capabilities}
              onChange={(e) => setCapabilities(e.target.value)}
              placeholder="Capabilities text for immediate search indexing"
              className="w-full min-h-36 rounded-md border border-input bg-background/70 px-3 py-2 text-sm"
            />
          </div>

          <div className="grid gap-1">
            <label htmlFor="ingest-token" className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Ingest Token
            </label>
            <Input
              id="ingest-token"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Optional unless auth is enforced"
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}
          {success && <p className="text-sm text-green-600">{success}</p>}

          <Button type="submit" disabled={submitting} className="w-full gap-2">
            {submitting ? <Loader2 className="size-4 animate-spin" /> : null}
            {submitting ? "Registering..." : "Register Product"}
          </Button>
        </form>
      </div>
    </main>
  )
}
