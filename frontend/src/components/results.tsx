import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { Code2, ExternalLink } from "lucide-react"

export type SearchCardResult = {
  id: string
  title: string
  snippet: string
  skills: string[]
  relevanceScore: number
  fileSource: string
  url?: string
}

export function SearchResultCard({ result }: { result: SearchCardResult }) {
  const scorePercent = (result.relevanceScore * 100).toFixed(0)
  
  return (
    <Card className="hover:shadow-xl hover:border-primary/50 transition-all duration-300 border-border bg-card/60 backdrop-blur-md group overflow-hidden relative">
      <div 
        className="absolute top-0 left-0 h-1 bg-gradient-to-r from-primary to-primary/40 transition-all duration-500" 
        style={{ width: `${scorePercent}%` }}
      />
      
      <CardHeader className="pb-3 pt-5">
        <div className="flex justify-between items-start gap-4">
          <div className="flex flex-col gap-1">
            <CardTitle className="text-xl text-foreground font-bold group-hover:text-primary transition-colors flex items-center gap-2">
              {result.title}
            </CardTitle>
            {result.url && (
              <a 
                href={result.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1 w-fit transition-colors"
              >
                {new URL(result.url).hostname}
                <ExternalLink className="size-3" />
              </a>
            )}
          </div>
          <Badge variant="outline" className="border-border text-muted shrink-0 bg-background/50">
            {result.fileSource}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <p className="text-sm text-foreground/80 line-clamp-3 mb-4 font-normal leading-relaxed">
          {result.snippet}
        </p>
        {result.skills.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {result.skills.map((skill) => (
              <Badge key={skill} variant="secondary" className="flex gap-1.5 items-center bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 py-1 transition-colors">
                <Code2 size={12} /> {skill}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>

      <CardFooter className="border-t border-border/50 pt-3 flex justify-between bg-muted/5 rounded-b-lg">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted font-medium">Match Score</span>
          <div className="w-16 h-2 rounded-full bg-muted overflow-hidden">
            <div className="h-full bg-primary" style={{ width: `${scorePercent}%` }} />
          </div>
          <span className="text-xs font-bold text-primary">{scorePercent}%</span>
        </div>
        <Button size="sm" variant="outline" className="text-xs gap-2 hover:bg-primary hover:text-primary-foreground transition-all">
          View Details
        </Button>
      </CardFooter>
    </Card>
  )
}