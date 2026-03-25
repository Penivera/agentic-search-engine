import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { Code2, Play } from "lucide-react"
import type { mockResultsType } from "../data/searchData"

export type SearchCardResult = {
  id: string
  title: string
  snippet: string
  skills: string[]
  relevanceScore: number
  fileSource: string
}

export function SearchResultCard({ result }: { result: mockResultsType | SearchCardResult }) {
  return (
    <Card className="hover:shadow-lg transition-all border-border bg-surface/20 backdrop-blur-sm group">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start gap-4">
          {/* Changed text-blue-600 to text-primary */}
          <CardTitle className="text-lg text-primary cursor-pointer hover:underline font-bold">
            {result.title}
          </CardTitle>
          <Badge variant="outline" className="border-border text-muted shrink-0">
            {result.fileSource}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <p className="text-sm text-muted line-clamp-2 mb-4 font-light leading-relaxed">
          {result.snippet}
        </p>
        <div className="flex flex-wrap gap-2 mt-3">
          {result.skills.map((skill) => (
            <Badge key={skill} variant="secondary" className="flex gap-1.5 items-center bg-primary/10 text-primary border-none py-1">
              <Code2 size={12} /> {skill}
            </Badge>
          ))}
        </div>
      </CardContent>

      {/* Replaced bg-slate-50/50 with bg-muted/5 and updated borders */}
      <CardFooter className="border-t border-border pt-3 flex justify-between bg-muted/5 rounded-b-lg">
        <span className="text-xs text-muted font-medium">
          Match: <span className="text-primary">{(result.relevanceScore * 100).toFixed(0)}%</span>
        </span>
        <Button size="sm" variant="ghost" className="text-xs gap-2 hover:bg-primary hover:text-white transition-colors">
          <Play size={14} fill="currentColor" /> Trigger Skill
        </Button>
      </CardFooter>
    </Card>
  )
}