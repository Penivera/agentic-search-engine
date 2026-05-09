import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowLeft, Loader2 } from "lucide-react"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { ThemeToggle } from "../components/ThemeToggle"
import HomeBackground from "../components/HomeBg"
import { registerPlatform, registerSkill } from "../services/api"

// --- 1. SOLANA IMPORTS ---
import { useWallet, useConnection } from "@solana/wallet-adapter-react"
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui"
import { Transaction, SystemProgram } from "@solana/web3.js"

export default function RegisterProduct() {
  const navigate = useNavigate()

  // --- 2. SOLANA HOOKS ---
  const { connection } = useConnection()
  const { publicKey, sendTransaction } = useWallet()

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

    // Safety check: Don't allow submission without a wallet
    if (!publicKey) {
      setError("Please connect your Solana wallet to register an agent.")
      return
    }

    setSubmitting(true)
    setError(null)
    setSuccess(null)

    try {
      // --- 3. THE WEB3 TRANSACTION ---
      // This creates a placeholder transaction that sends 0 SOL to the user's own wallet.
      // It triggers the Phantom approval popup to prove the Web3 integration works.
      // TODO: Replace this block with your teammate's actual Smart Contract instruction later.
      const transaction = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: publicKey,
          toPubkey: publicKey,
          lamports: 100,
        })
      );

      // Ask the user to sign the transaction and wait for the network to confirm it
      const signature = await sendTransaction(transaction, connection);
      await connection.confirmTransaction(signature, 'processed');


      // --- 4. THE WEB2 DATABASE STORAGE ---
      // Once the blockchain confirms the transaction, we save the data to your indexer.
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

      setSuccess("Agent successfully registered on Solana and indexed for search.")
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

        <div className="fixed top-4 left-4 z-50">
          <Button variant="ghost" size="sm" onClick={() => navigate("/")} className="gap-2">
            <ArrowLeft className="size-4" />
            <span className="hidden sm:inline">Back</span>
          </Button>
        </div>

        <div className="fixed top-4 right-4 z-50">
          <ThemeToggle />
        </div>

        <h1 className="text-4xl font-bold tracking-tight mb-2 mt-10 sm:mt-0">Register Agentic Product</h1>
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


          <div className="pt-4">
            {!publicKey ? (
              <div className="w-full rounded-lg  bg-purple-500/5 flex [&_.wallet-adapter-dropdown]:w-full [&_.wallet-adapter-dropdown]:flex [&_.wallet-adapter-button]:w-full!">
                <WalletMultiButton 
                  style={{ 
                    background: 'linear-gradient(to right, #9333ea, #2563eb)', 
                    height: '3rem', 
                    fontSize: '1.125rem',
                    width: '100%', 
                    justifyContent: 'center' 
                  }} 
                />
              </div>
            ) : (
              <Button
                type="submit"
                disabled={submitting}
                className="w-full gap-2 bg-linear-to-r from-purple-600 to-blue-600 hover:opacity-90 text-white font-bold h-12 text-lg"
              >
                {submitting ? <Loader2 className="size-5 animate-spin" /> : null}
                {submitting ? "Awaiting Signature..." : "Sign Transaction & Register"}
              </Button>
            )}
          </div>
        </form>
      </div>
    </main>
  )
}
