import { useMemo } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="border border-graphite-600 bg-graphite-900 px-3 py-2 shadow-none">
      <p className="font-mono text-[11px] text-paper-500">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} className="font-mono text-xs" style={{ color: p.color }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  )
}

/**
 * A 90-day trend line comparing raw daily signal counts across all three
 * pillars at once — the comparative view the calendar heatmap (one
 * pillar at a time) intentionally doesn't show.
 */
export default function TrendChart({ history, pillars }) {
  const data = useMemo(() => {
    if (!history?.length) return []
    // Thin to every 3rd day for a legible 90-day line without visual noise.
    return history
      .filter((_, i) => i % 3 === 0)
      .map((d) => ({
        ...d,
        label: new Date(d.date + 'T00:00:00Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }))
  }, [history])

  if (!data.length) return null

  return (
    <div className="border border-graphite-600 bg-graphite-900/60 px-5 py-5">
      <header className="mb-4">
        <h3 className="text-sm font-medium text-paper-100">Pillars compared</h3>
        <p className="mt-0.5 text-xs text-paper-500">Daily signal counts, all three pillars, trailing 90 days.</p>
      </header>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: '#8B9199', fontSize: 10, fontFamily: 'IBM Plex Mono, monospace' }}
            axisLine={{ stroke: '#2A323B' }}
            tickLine={false}
            interval={Math.floor(data.length / 6)}
          />
          <YAxis
            tick={{ fill: '#8B9199', fontSize: 10, fontFamily: 'IBM Plex Mono, monospace' }}
            axisLine={false}
            tickLine={false}
            width={28}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#3C4652' }} />
          {pillars.map((p) => (
            <Line
              key={p.key}
              type="monotone"
              dataKey={p.key}
              name={p.shortLabel}
              stroke={p.accent}
              strokeWidth={1.75}
              dot={false}
              activeDot={{ r: 3 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
