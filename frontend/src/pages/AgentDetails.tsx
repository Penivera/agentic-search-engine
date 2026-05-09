import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { ArrowLeft, Loader2, ExternalLink, Terminal, Copy, CheckCircle2 } from "lucide-react"
import { Button } from "../../src/components/ui/button"
import { Badge } from "../../src/components/ui/badge"
import { ThemeToggle } from "../../src/components/ThemeToggle"
import HomeBackground from "../../src/components/HomeBg"
import { getSkillDetails } from "../services/api"

export default function AgentDetails() {
    const { id } = useParams()
    const navigate = useNavigate()

    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [agent, setAgent] = useState<any>(null)
    const [copied, setCopied] = useState(false)

    useEffect(() => {
        const fetchAgent = async () => {
            if (!id) return

            try {
                setLoading(true)
                const data = await getSkillDetails(id)
                setAgent(data)
            } catch (err) {
                setError("Failed to load agent details. It may have been removed.")
                console.error(err)
            } finally {
                setLoading(false)
            }
        }

        fetchAgent()
    }, [id])



    const copyToClipboard = async () => {
        const textToCopy = agent?.skill?.capabilities || agent?.capabilities || "No capabilities defined.";

        try {
            if (navigator?.clipboard?.writeText) {
                await navigator.clipboard.writeText(textToCopy);
            } else {
                const textArea = document.createElement("textarea");
                textArea.value = textToCopy;

                textArea.style.position = "fixed";
                textArea.style.left = "-999999px";
                textArea.style.top = "-999999px";

                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();

                document.execCommand('copy');
                textArea.remove();
            }

            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error("Failed to copy text: ", err);
            alert("Failed to copy to clipboard. Please copy manually.");
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex flex-col items-center justify-center">
                <Loader2 className="size-12 animate-spin text-primary mb-4" />
                <h2 className="text-xl font-bold">Decoding SKILL.md...</h2>
            </div>
        )
    }

    if (error || !agent) {
        return (
            <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
                <div className="text-center p-8 border border-red-500/20 bg-red-500/5 rounded-2xl max-w-md">
                    <p className="text-red-500 font-bold mb-2">Error 404</p>
                    <p className="text-muted-foreground mb-6">{error || "Agent not found in the index."}</p>
                    <Button onClick={() => navigate("/search")}>Back to Search</Button>
                </div>
            </div>
        )
    }

    const platformName = agent.platform?.name || agent.platform_name || agent.skill?.skill_name || agent.skill_name || agent.name || "Unknown Agent"
    const description = agent.platform?.description || agent.platform_description || agent.description  || agent.skill?.description  || "No description provided."
    const platformUrl = agent.platform?.url || "#"
    const rawCapabilities = agent.skill?.capabilities || agent.capabilities || "No capabilities defined."
    const formatCapabilities = (raw: any) => {
        if (!raw) return "No capabilities defined.";
        if (typeof raw === 'object') return JSON.stringify(raw, null, 2);

        let text = String(raw).trim();
        let header = "";

        const capIndex = text.toLowerCase().indexOf("capabilities:");

        if (capIndex !== -1) {
            const exactMatchLength = "capabilities:".length;
            header = text.substring(0, capIndex + exactMatchLength).trim() + "\n\n";

            text = text.substring(capIndex + exactMatchLength).trim();
        }

        if (text.includes(';')) {
            return header + "- " + text.split(';').map(item => item.trim()).filter(Boolean).join('\n- ');
        }

        return header + "- " + text.trim();
    };
    const capabilities = formatCapabilities(rawCapabilities);

    const tags = agent.skill?.tags || agent.tags || ["AI", "Agent"]

    return (
        <div className="relative min-h-screen overflow-x-hidden bg-background text-foreground pb-20">
            <HomeBackground />

            <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/60 backdrop-blur-xl">
                <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
                    <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="fixed top-4 left-4 gap-2">
                        <ArrowLeft className="size-4" /> Back
                    </Button>
                    <ThemeToggle />
                </div>
            </header>

            <main className="relative z-10 max-w-5xl mx-auto px-4 pt-8">
                <div className="flex flex-col md:flex-row gap-6 items-start justify-between mb-10">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-4xl font-bold tracking-tight">{platformName}</h1>
                            <Badge variant="secondary" className="bg-primary/10 text-primary border-none">
                                Verified
                            </Badge>
                        </div>
                        <p className="text-lg text-muted-foreground max-w-2xl">
                            {description}
                        </p>

                        <div className="flex flex-wrap gap-2 mt-4">
                            {tags.map((tag: string, i: number) => (
                                <Badge key={i} variant="outline" className="border-primary/30 text-primary">
                                    {tag}
                                </Badge>
                            ))}
                        </div>
                    </div>

                    <div className="flex flex-col gap-3 w-full md:w-auto">
                        <a href={platformUrl} target="_blank" rel="noreferrer" className="w-full">
                            <Button className="w-full md:w-48 gap-2 bg-linear-to-r from-purple-600 to-blue-600">
                                <ExternalLink className="size-4" /> Visit Platform
                            </Button>
                        </a>
                        <div className="text-xs text-center text-muted-foreground font-mono bg-muted/20 py-2 rounded-md border border-border">
                            ID: {id?.substring(0, 12)}...
                        </div>
                    </div>
                </div>

                <div className="rounded-xl border border-border bg-card/50 backdrop-blur-sm overflow-hidden shadow-2xl">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-muted/30">
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                            <Terminal className="size-4" />
                            <span>SKILL.md</span>
                        </div>
                        <Button variant="ghost" size="sm" onClick={copyToClipboard} className="h-8 gap-2 hover:text-primary">
                            {copied ? <CheckCircle2 className="size-4 text-green-500" /> : <Copy className="size-4" />}
                            {copied ? "Copied!" : "Copy YAML"}
                        </Button>
                    </div>

                    <div className="p-6 overflow-x-auto">
                        <pre className="font-mono text-sm leading-relaxed text-foreground/80 whitespace-pre-wrap">
                            {capabilities}
                        </pre>
                    </div>
                </div>
            </main>
        </div>
    )
}