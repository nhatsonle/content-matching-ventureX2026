import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export function ChartSkeleton({ tall = false }: { tall?: boolean }) {
  return <Skeleton className={tall ? 'h-72 w-full' : 'h-56 w-full'} />
}

export function TableSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-4 gap-3">
        {Array.from({ length: 4 }).map((_, index) => (
          <Skeleton key={index} className="h-4 w-full" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="grid grid-cols-4 gap-3">
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-full" />
        </div>
      ))}
    </div>
  )
}

export function MatchResultsSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      {/* Top Stats */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-3 w-12" />
      </div>

      <div className="pl-3 border-l-2 border-muted">
        <Skeleton className="h-4 w-4/5" />
      </div>

      <hr className="border-t border-muted/20" />

      {/* Navigation Controls Skeleton */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-28" />
        <div className="flex gap-2">
          <Skeleton className="h-8 w-8 rounded-full" />
          <Skeleton className="h-8 w-8 rounded-full" />
        </div>
      </div>

      {/* Single Candidate Card Skeleton */}
      <Card>
        <CardContent className="flex flex-col gap-4 p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex flex-col gap-2">
              <Skeleton className="h-5 w-36" />
              <Skeleton className="h-3 w-28" />
            </div>
            <Skeleton className="size-12 rounded-full" />
          </div>
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <div className="grid grid-cols-2 gap-3">
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-full" />
          </div>
        </CardContent>
      </Card>

      {/* Dot Indicators Skeleton */}
      <div className="flex justify-center gap-1.5 mt-2">
        <Skeleton className="h-1.5 w-6 rounded-full" />
        <Skeleton className="h-1.5 w-1.5 rounded-full" />
        <Skeleton className="h-1.5 w-1.5 rounded-full" />
        <Skeleton className="h-1.5 w-1.5 rounded-full" />
        <Skeleton className="h-1.5 w-1.5 rounded-full" />
      </div>
    </div>
  )
}
