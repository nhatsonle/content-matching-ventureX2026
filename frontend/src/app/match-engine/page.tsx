'use client'

import { useState, useEffect } from 'react'
import type { MatchResponse } from '@/lib/data/types'
import PageHeader from '@/components/layout/PageHeader'
import BriefForm from '@/components/match-engine/BriefForm'
import CandidateCard from '@/components/match-engine/CandidateCard'
import { MatchResultsSkeleton } from '@/components/shared/PageSkeleton'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function MatchEnginePage() {
  const [result, setResult] = useState<MatchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeIdx, setActiveIdx] = useState(0)

  // Load result from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('match_engine_result')
    if (saved) {
      try {
        setResult(JSON.parse(saved))
      } catch (e) {
        console.error('Failed to parse saved match engine results:', e)
      }
    }
  }, [])

  const handleResult = (data: MatchResponse) => {
    setResult(data)
    localStorage.setItem('match_engine_result', JSON.stringify(data))
    setLoading(false)
    setActiveIdx(0)
  }

  return (
    <div className="max-w-4xl">
      <PageHeader
        title="Match Engine"
        description="AI-powered director matching — fill in your campaign brief to get a shortlist of best-fit directors."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div>
          <BriefForm
            onResult={handleResult}
            onLoading={setLoading}
          />
        </div>

        {/* Results */}
        <div>
          {loading && <MatchResultsSkeleton />}

          {!loading && result && result.shortlist.length > 0 && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  {result.total_candidates_considered} candidates considered
                </p>
                <p className="text-xs text-muted-foreground">
                  {result.response_time_ms?.toFixed(0)}ms
                </p>
              </div>

              {result.brief_summary && (
                <p className="text-sm border-l-2 border-black pl-3 text-muted-foreground italic">
                  {result.brief_summary}
                </p>
              )}

              <Separator />

              {/* Slider / Carousel Container */}
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium">
                    Candidate {activeIdx + 1} of {result.shortlist.length}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8 rounded-full shadow-sm hover:bg-accent"
                      onClick={() => setActiveIdx(prev => Math.max(0, prev - 1))}
                      disabled={activeIdx === 0}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8 rounded-full shadow-sm hover:bg-accent"
                      onClick={() => setActiveIdx(prev => Math.min(result.shortlist.length - 1, prev + 1))}
                      disabled={activeIdx === result.shortlist.length - 1}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* Active Candidate Card with Transition */}
                <div key={activeIdx} className="transition-all duration-300 ease-in-out animate-in fade-in slide-in-from-right-4">
                  <CandidateCard candidate={result.shortlist[activeIdx]} />
                </div>

                {/* Dots Pagination Indicator */}
                <div className="flex justify-center gap-1.5 mt-2">
                  {result.shortlist.map((_, idx) => (
                    <button
                      key={idx}
                      className={`h-1.5 rounded-full transition-all duration-300 ${
                        idx === activeIdx ? 'w-6 bg-black dark:bg-white' : 'w-1.5 bg-muted-foreground/30'
                      }`}
                      onClick={() => setActiveIdx(idx)}
                      title={`Go to candidate ${idx + 1}`}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          {!loading && !result && (
            <div className="flex items-center justify-center h-48 border border-dashed rounded-lg text-muted-foreground text-sm">
              Submit a brief to see matching results
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
