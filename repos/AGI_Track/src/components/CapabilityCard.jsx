import { useEffect, useState } from 'react'
import { CheckCircle2, CircleDashed, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'
import { useI18n } from '../i18n.jsx'

const VERIFICATION_STYLES = {
  verified: {
    icon: CheckCircle2,
    label: 'Verified',
    className: 'text-signal-cyan border-signal-cyan/40 bg-signal-cyan/10'
  },
  pending: {
    icon: CircleDashed,
    label: 'Pending review',
    className: 'text-paper-500 border-paper-500/30 bg-transparent'
  }
}

function Delta({ value }) {
  if (value === null || value === undefined) return null
  const isFlat = Math.abs(value) < 0.05
  const isUp = value > 0
  const Icon = isFlat ? Minus : isUp ? ArrowUpRight : ArrowDownRight
  const color = isFlat ? 'text-paper-500' : isUp ? 'text-signal-cyan' : 'text-signal-rose'
  return (
    <span className={`inline-flex items-center gap-0.5 font-mono text-xs ${color}`}>
      <Icon size={12} strokeWidth={2.5} />
      {isFlat ? '0.0' : Math.abs(value).toFixed(1)}
    </span>
  )
}

export default function CapabilityCard({
  icon: Icon,
  accent,
  pillar,
  score,
  deltaToday,
  delta7d,
  summary,
  breakthrough,
  everydayImpact
}) {
  const { t, isArabic, translateDynamic } = useI18n()
  const [trSummary, setTrSummary] = useState(null)
  const [trImpact, setTrImpact] = useState(null)

  useEffect(() => {
    if (isArabic) {
      if (summary) translateDynamic(summary).then(setTrSummary)
      if (everydayImpact) translateDynamic(everydayImpact).then(setTrImpact)
    }
  }, [isArabic, summary, everydayImpact, translateDynamic])

  const verification = breakthrough ? VERIFICATION_STYLES[breakthrough.verification_status] : null
  const VerificationIcon = verification?.icon

  return (
    <article className="relative flex flex-col border border-graphite-600 bg-graphite-900/60">
      <div className={`absolute ${isArabic ? 'right-0' : 'left-0'} top-0 h-full w-[3px]`} style={{ backgroundColor: accent }} />

      <header className={`flex items-start justify-between gap-3 border-b border-graphite-700 px-5 py-4 ${isArabic ? 'pr-6' : 'pl-6'}`}>
        <div className="flex items-center gap-2.5">
          <Icon size={17} strokeWidth={1.75} style={{ color: accent }} />
          <h3 className="text-sm font-medium text-paper-100">{t(pillar)}</h3>
        </div>
        {score !== null && (
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-xl tabular text-paper-100">{score.toFixed(1)}</span>
            <Delta value={deltaToday} />
          </div>
        )}
      </header>

      <div className={`flex flex-1 flex-col gap-4 px-5 py-4 ${isArabic ? 'pr-6' : 'pl-6'}`}>
        <p className="text-sm leading-relaxed text-paper-300">
          {isArabic ? (trSummary || summary) : summary}
        </p>

        {breakthrough && (
          <div className="border border-graphite-700 bg-graphite-950/60 p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="font-mono text-[11px] text-paper-500">{t('Latest signal')}</span>
              {verification && (
                <span className={`flex items-center gap-1 border px-1.5 py-0.5 font-mono text-[10px] ${verification.className}`}>
                  <VerificationIcon size={11} />
                  {t(verification.label)}
                </span>
              )}
            </div>
            <p className="mt-1.5 text-sm text-paper-100">{breakthrough.topic || breakthrough.title}</p>
            {breakthrough.supporting_evidence?.[0] ? (
              <span className="mt-2 text-xs font-mono text-paper-500 break-all line-clamp-1 opacity-80">
                {breakthrough.supporting_evidence[0]}
              </span>
            ) : breakthrough.source_url ? (
              <a
                href={breakthrough.source_url}
                target="_blank"
                rel="noreferrer"
                className="mt-2 inline-block break-all font-mono text-xs text-paper-500 underline decoration-graphite-500 underline-offset-2 hover:text-signal-cyan"
              >
                {t('View Source')}
              </a>
            ) : null}
          </div>
        )}

        {everydayImpact && (
          <div className="mt-auto pt-1">
            <span className="font-mono text-[11px] text-paper-500">{t('Impact on everyday life')}</span>
            <p className="mt-1 text-sm leading-relaxed text-paper-300">
              {isArabic ? (trImpact || everydayImpact) : everydayImpact}
            </p>
          </div>
        )}

        {delta7d !== null && delta7d !== undefined && (
          <div className="flex items-center justify-between border-t border-graphite-700 pt-3 font-mono text-[11px] text-paper-500">
            <span>{t('7-day trend')}</span>
            <Delta value={delta7d} />
          </div>
        )}
      </div>
    </article>
  )
}
