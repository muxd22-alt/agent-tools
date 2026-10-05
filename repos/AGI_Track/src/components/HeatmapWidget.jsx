import { useMemo, useState } from 'react'

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function intensityClass(value, max, accent) {
  if (!value || max === 0) return { backgroundColor: 'rgba(255,255,255,0.04)' }
  const ratio = value / max
  const step = ratio > 0.75 ? 1 : ratio > 0.5 ? 0.7 : ratio > 0.25 ? 0.42 : 0.22
  return { backgroundColor: accent, opacity: step }
}

/**
 * A GitHub-style calendar heatmap showing daily signal velocity (commits,
 * papers, releases) for a single research pillar across the trailing
 * ~90 days. `history` is the `days` array from historical_trends.json.
 */
export default function HeatmapWidget({ history, pillars, activePillar, onChangePillar }) {
  const current = pillars.find((p) => p.key === activePillar) ?? pillars[0]

  const { weeks, max, total, monthMarks } = useMemo(() => {
    if (!history?.length) return { weeks: [], max: 0, total: 0, monthMarks: [] }

    const days = history.map((d) => ({ ...d, dateObj: new Date(d.date + 'T00:00:00Z') }))
    const firstDow = days[0].dateObj.getUTCDay()
    const padded = [...Array(firstDow).fill(null), ...days]

    const weeksArr = []
    for (let i = 0; i < padded.length; i += 7) {
      weeksArr.push(padded.slice(i, i + 7))
    }

    const values = days.map((d) => d[current.key] ?? 0)
    const maxVal = Math.max(1, ...values)
    const totalVal = values.reduce((a, b) => a + b, 0)

    const marks = []
    let lastMonth = -1
    weeksArr.forEach((week, wi) => {
      const firstReal = week.find((d) => d)
      if (firstReal) {
        const m = firstReal.dateObj.getUTCMonth()
        if (m !== lastMonth) {
          marks.push({ week: wi, label: MONTH_LABELS[m] })
          lastMonth = m
        }
      }
    })

    return { weeks: weeksArr, max: maxVal, total: totalVal, monthMarks: marks }
  }, [history, current.key])

  return (
    <div className="border border-graphite-600 bg-graphite-900/60">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-graphite-700 px-5 py-4">
        <div>
          <h3 className="text-sm font-medium text-paper-100">Signal velocity — trailing 90 days</h3>
          <p className="mt-0.5 text-xs text-paper-500">
            Daily count of {current.unit} · <span className="font-mono tabular">{total}</span> total
          </p>
        </div>
        <div className="flex gap-1 border border-graphite-700 p-0.5">
          {pillars.map((p) => (
            <button
              key={p.key}
              onClick={() => onChangePillar(p.key)}
              className={`px-2.5 py-1 text-xs font-medium transition-colors ${
                p.key === current.key ? 'bg-graphite-700 text-paper-100' : 'text-paper-500 hover:text-paper-100'
              }`}
              style={p.key === current.key ? { boxShadow: `inset 0 -2px 0 ${p.accent}` } : undefined}
            >
              {p.shortLabel}
            </button>
          ))}
        </div>
      </header>

      <div className="overflow-x-auto px-5 py-5">
        <div className="inline-flex flex-col gap-2" style={{ minWidth: `${weeks.length * 15 + 32}px` }}>
          <div className="flex text-[10px] text-paper-500" style={{ paddingLeft: '28px' }}>
            {weeks.map((_, wi) => {
              const mark = monthMarks.find((m) => m.week === wi)
              return (
                <div key={wi} className="w-[15px] shrink-0 font-mono">
                  {mark ? mark.label : ''}
                </div>
              )
            })}
          </div>

          <div className="flex gap-1.5">
            <div className="flex flex-col gap-[3px] pr-1 text-[10px] text-paper-500">
              {DAY_LABELS.map((d, i) => (
                <div key={d} className="h-[13px] leading-[13px]">
                  {i % 2 === 1 ? d.slice(0, 1) : ''}
                </div>
              ))}
            </div>
            <div className="flex gap-[3px]">
              {weeks.map((week, wi) => (
                <div key={wi} className="flex flex-col gap-[3px]">
                  {week.map((day, di) =>
                    day ? (
                      <div
                        key={di}
                        title={`${day.date} · ${day[current.key] ?? 0} ${current.unit}`}
                        className="h-[13px] w-[13px] border border-graphite-950"
                        style={intensityClass(day[current.key], max, current.accent)}
                      />
                    ) : (
                      <div key={di} className="h-[13px] w-[13px]" />
                    )
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-1.5 pt-1 pl-7 text-[10px] text-paper-500">
            <span>Less</span>
            {[0.15, 0.3, 0.55, 0.8, 1].map((op, i) => (
              <div key={i} className="h-[10px] w-[10px] border border-graphite-950" style={{ backgroundColor: current.accent, opacity: op }} />
            ))}
            <span>More</span>
          </div>
        </div>
      </div>
    </div>
  )
}
