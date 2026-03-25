import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowLeft, Loader2 } from "lucide-react"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { ThemeToggle } from "../components/ThemeToggle"
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
          skills_url: skillsUrl || undefined,
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
    <main className="min-h-screen bg-background text-foreground px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" size="sm" onClick={() => navigate("/home")} className="gap-2">
            <ArrowLeft className="size-4" /> Back
          </Button>
          <ThemeToggle />
        </div>

        <h1 className="text-3xl font-bold mb-2">Register Agentic Product</h1>
        <p className="text-muted-foreground mb-6">
          Add your product so humans can discover it in semantic search.
        </p>

        <form onSubmit={onSubmit} className="space-y-4 rounded-xl border border-border p-5 bg-card/50">
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Product name" required />
          <Input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="Product URL (https://...)" required />
          <Input
            value={homepageUri}
            onChange={(e) => setHomepageUri(e.target.value)}
            placeholder="Homepage URL (https://...)"
            required
          />
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short description"
          />
          <Input
            value={skillsUrl}
            onChange={(e) => setSkillsUrl(e.target.value)}
            placeholder="SKILL.md URL (optional)"
          />

          <div className="pt-2 border-t border-border" />

          <Input
            value={skillName}
            onChange={(e) => setSkillName(e.target.value)}
            placeholder="Primary skill name (optional)"
          />
          <Input
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="Tags comma-separated (optional): search, wallet, automation"
          />
          <textarea
            value={capabilities}
            onChange={(e) => setCapabilities(e.target.value)}
            placeholder="Capabilities text (recommended for immediate search indexing)"
            className="w-full min-h-32 rounded-md border border-input bg-background px-3 py-2 text-sm"
          />

          <Input
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Ingest token (optional; required only if server enforces auth)"
          />

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
