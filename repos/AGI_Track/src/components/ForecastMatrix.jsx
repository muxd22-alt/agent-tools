import { useEffect, useState } from 'react'
import { useI18n } from '../i18n.jsx'

const IMPACT_STYLES = {
  Low: 'text-paper-500 border-paper-500/30',
  Medium: 'text-signal-amber border-signal-amber/40',
  High: 'text-signal-rose border-signal-rose/40',
  Critical: 'text-signal-rose border-signal-rose/60 bg-signal-rose/10'
}

const ROWS = [
  { key: '30_days', label: '30 days' },
  { key: '90_days', label: '90 days' },
  { key: '365_days', label: '365 days' }
]

export default function ForecastMatrix({ forecast }) {
  const { t, isArabic, translateDynamic } = useI18n()
  const [translations, setTranslations] = useState({})

  useEffect(() => {
    if (isArabic && forecast) {
      const promises = ROWS.map(async (row) => {
        const entry = forecast?.[row.key]
        if (entry?.milestone) {
          const tr = await translateDynamic(entry.milestone)
          return [row.key, tr]
        }
        return [row.key, null]
      })
      Promise.all(promises).then((results) => {
        setTranslations(Object.fromEntries(results.filter(([, v]) => v)))
      })
    }
  }, [isArabic, forecast, translateDynamic])

  return (
    <div className="border border-graphite-600 bg-graphite-900/60">
      <header className="border-b border-graphite-700 px-5 py-4">
        <h3 className="text-sm font-medium text-paper-100">{t('Forecast matrix')}</h3>
        <p className="mt-0.5 text-xs text-paper-500">
          {t('Projected, not measured — extrapolated from the momentum above.')}
        </p>
      </header>
      <div>
        {ROWS.map((row, i) => {
          const entry = forecast?.[row.key]
          if (!entry) return null
          
          // Determine impact aesthetically since the new API provides just strings
          let autoImpact = 'Medium'
          if (row.key === '90_days') autoImpact = 'High'
          if (row.key === '365_days') autoImpact = 'Critical'

          return (
            <div
              key={row.key}
              className={`flex flex-col gap-2 px-5 py-4 sm:grid sm:grid-cols-[72px_1fr_auto] sm:items-center sm:gap-4 ${
                i !== ROWS.length - 1 ? 'border-b border-graphite-700' : ''
              }`}
            >
              <div className="flex items-center justify-between sm:contents">
                <span className="font-mono text-xs text-paper-500">{t(row.label)}</span>
                <span
                  className={`whitespace-nowrap border px-2 py-1 font-mono text-[11px] sm:order-3 ${
                    IMPACT_STYLES[autoImpact]
                  }`}
                >
                  {t(autoImpact)}
                </span>
              </div>
              <p className="text-sm leading-relaxed text-paper-300">
                {isArabic ? (translations[row.key] || entry) : entry}
              </p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
