import { NextResponse } from 'next/server'

export const maxDuration = 120 // allow up to 2 minutes for slow LLM responses

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'
    const res = await fetch(`${backendUrl}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(120_000), // 2 minute timeout
    })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    console.error('[/api/match] Backend error:', message)
    return NextResponse.json({ error: `Backend unavailable: ${message}` }, { status: 503 })
  }
}
