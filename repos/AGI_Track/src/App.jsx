import { useEffect, useState } from 'react'
import {
  FlaskConical,
  Sigma,
  Cpu,
  Compass,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Sparkles,
  Activity,
  Layers,
  TrendingUp,
  Target,
  ShieldCheck,
  Zap,
  CircleDashed
} from 'lucide-react'
import { useI18n } from './i18n.jsx'
import Header from './components/Header.jsx'
import Footer from './components/Footer.jsx'
import CapabilityCard from './components/CapabilityCard.jsx'
import HeatmapWidget from './components/HeatmapWidget.jsx'
import TrendChart from './components/TrendChart.jsx'
import ForecastMatrix from './components/ForecastMatrix.jsx'
import SignalFeed from './components/SignalFeed.jsx'
import VerifyPalette from './components/VerifyPalette.jsx'

const PILLAR_META = {
  scientific_rd: { icon: FlaskConical, accent: '#9A8CFF', shortLabel: 'Sci R&D', unit: 'papers' },
  math_proofs: { icon: Sigma, accent: '#4FD1C5', shortLabel: 'Math', unit: 'commits' },
  software_systems: { icon: Cpu, accent: '#F5A623', shortLabel: 'Software', unit: 'PRs' }
}

const BASE = import.meta.env.BASE_URL

function useJson(path) {
  const [state, setState] = useState({ data: null, error: null, loading: true })

  useEffect(() => {
    let cancelled = false
    fetch(`${BASE}${path}?t=${Date.now()}`)
      .then((res) => {
        if (!res.ok) throw new Error(`${path} responded ${res.status}`)
        return res.json()
      })
      .then((data) => !cancelled && setState({ data, error: null, loading: false }))
      .catch((error) => !cancelled && setState({ data: null, error, loading: false }))
    return () => {
      cancelled = true
    }
  }, [path])

  return state
}

function SectionHeader({ icon: Icon, title, badge }) {
  const { t } = useI18n()
  return (
    <div className="flex items-center justify-between border-b border-graphite-800 pb-3 pt-4">
      <div className="flex items-center gap-2.5">
        <div className="flex h-7 w-7 items-center justify-center rounded border border-graphite-700 bg-graphite-900/80 text-signal-amber">
          <Icon size={15} strokeWidth={2} />
        </div>
        <h2 className="font-mono text-sm font-semibold tracking-wide text-paper-100 uppercase">
          {t(title)}
        </h2>
      </div>
      {badge && (
        <span className="font-mono text-[10px] uppercase tracking-wider text-paper-500 bg-graphite-900 border border-graphite-700 px-2 py-0.5 rounded">
          {t(badge)}
        </span>
      )}
    </div>
  )
}

function ExecutiveCommandCenter({ decision, protocol, kpis }) {
  const { t, isArabic, translateDynamic } = useI18n()
  const [translatedBrief, setTranslatedBrief] = useState(null)
  
  useEffect(() => {
    if (isArabic && decision?.executive_brief) {
      translateDynamic(decision.executive_brief).then(setTranslatedBrief)
    }
  }, [isArabic, decision?.executive_brief, translateDynamic])

  if (!decision) return null

  return (
    <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
      {/* Executive Brief Box */}
      <div className="relative overflow-hidden border border-signal-amber/30 bg-gradient-to-br from-signal-amber/[0.08] via-graphite-900/90 to-graphite-950 p-6 shadow-[0_0_30px_rgba(245,166,35,0.05)]">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(245,166,35,0.12),transparent_70%)]" />
        <div className="relative flex flex-col gap-4">
          <div className="flex items-start gap-4">
            <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-signal-amber/30 bg-signal-amber/10 shadow-[0_0_15px_rgba(245,166,35,0.2)]">
              <Sparkles size={18} className="text-signal-amber" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="font-mono text-xs font-bold uppercase tracking-widest text-signal-amber">
                  {t('Executive Brief')}
                </span>
                {protocol && (
                  <span className="rounded-full border border-graphite-700 bg-graphite-800/80 px-2.5 py-0.5 font-mono text-[10px] text-paper-400">
                    {protocol}
                  </span>
                )}
                <span className="flex items-center gap-1 ml-auto rounded-full border border-signal-cyan/50 bg-signal-cyan/10 px-2.5 py-0.5 font-mono text-[10px] text-signal-cyan">
                  <Cpu size={11} className="text-signal-cyan" />
                  {t('OpenRouter Analytical Layer')}
                </span>
              </div>
              <p className="mt-2.5 text-base leading-relaxed font-medium text-paper-100">
                {isArabic ? (translatedBrief || decision.executive_brief) : decision.executive_brief}
              </p>
              <div className="mt-4 border-t border-signal-amber/20 pt-3 flex items-center justify-between text-xs text-paper-400">
                 <span className="font-mono text-xs">{t('Daily AI Reasoner & Future Forecast Helper')}</span>
                 <span className="font-mono opacity-60">Status: Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Regime and Status Strip */}
      <div className="grid grid-cols-2 gap-3">
        <div className="border border-graphite-700 bg-graphite-900/40 p-4 flex flex-col items-start justify-center">
          <span className="font-mono text-[11px] text-paper-500 mb-1">{t('Market / Intelligence Regime')}</span>
          <span className="font-mono text-lg font-semibold text-signal-cyan">{decision.regime}</span>
        </div>
        <div className="border border-graphite-700 bg-graphite-900/40 p-4 flex flex-col items-start justify-center">
          <span className="font-mono text-[11px] text-paper-500 mb-1">{t('Signal Velocity')}</span>
          <span className="font-mono text-lg font-semibold text-paper-100">{decision.signal_velocity}</span>
        </div>
        <div className="border border-graphite-700 bg-graphite-900/40 p-4 flex flex-col items-start justify-center">
          <span className="font-mono text-[11px] text-paper-500 mb-1">{t('Confidence')}</span>
          <span className="font-mono text-lg font-semibold text-emerald-400">{decision.confidence}%</span>
        </div>
        <div className="border border-graphite-700 bg-graphite-900/40 p-4 flex flex-col items-start justify-center">
          <span className="font-mono text-[11px] text-paper-500 mb-1">{t('Strategic Bias')}</span>
          <span className="font-mono text-lg font-semibold text-signal-amber">{decision.strategic_bias}</span>
        </div>
      </div>
    </div>
  )
}

function CompositeIndex({ composite, kpis }) {
  const { t } = useI18n()

  if (!composite) return null
  const isUp = composite.delta_7d > 0
  const isFlat = Math.abs(composite.delta_7d) < 0.05
  const DeltaIcon = isFlat ? Minus : isUp ? ArrowUpRight : ArrowDownRight

  const kpiLabels = {
    'signal_coverage': 'Signal Coverage',
    'source_diversity': 'Source Diversity',
    'evidence_freshness': 'Evidence Freshness',
    'duplicate_rate': 'Duplicate Rate',
    'ai_agreement': 'AI Agreement',
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
      {/* Primary Metric Score Card */}
      <div className="border border-graphite-600 bg-graphite-900/60 p-6 sm:p-7 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-paper-500 uppercase tracking-wider">{t('Composite horizon index')}</span>
            <span className="inline-flex items-center gap-1 border border-signal-cyan/30 bg-signal-cyan/10 px-2 py-0.5 font-mono text-[11px] text-signal-cyan">
              <Zap size={11} /> Live Benchmark
            </span>
          </div>
          <div className="mt-4 flex items-baseline gap-4">
            <span className="font-mono text-6xl sm:text-7xl font-bold tabular tracking-tight text-paper-100">
              {composite.score.toFixed(1)}
            </span>
            <div className="flex flex-col">
              <span
                className={`flex items-center gap-1 font-mono text-base font-medium ${
                  isFlat ? 'text-paper-500' : isUp ? 'text-signal-cyan' : 'text-signal-rose'
                }`}
              >
                <DeltaIcon size={18} strokeWidth={2.5} />
                {Math.abs(composite.delta_7d).toFixed(1)} {t('this week')}
              </span>
              <span className="font-mono text-xs text-paper-500">7-Day Trajectory</span>
            </div>
          </div>
        </div>
        <p className="mt-6 border-t border-graphite-800 pt-4 text-xs leading-relaxed text-paper-500">
          {t('Unweighted average of the three tracked pillars below, each scored 0–100 against its own historical baseline. A heuristic momentum gauge, not a forecast of arrival.')}
        </p>
      </div>

      {/* BI KPI Strip */}
      {kpis && (
        <div className="grid grid-rows-5 gap-2">
          {Object.entries(kpis).map(([key, val]) => (
            <div key={key} className="border border-graphite-700 bg-graphite-900/40 px-4 py-2 flex items-center justify-between">
              <span className="font-mono text-[11px] text-paper-500 uppercase">{t(kpiLabels[key] || key)}</span>
              <span className="font-mono text-sm font-semibold text-paper-100">{val}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function App() {
  const { t, isArabic, dir } = useI18n()
  const { data: latest, error: latestError, loading: latestLoading } = useJson('data/latest_data.json')
  const { data: trends } = useJson('data/historical_trends.json')
  const [activeTab, setActiveTab] = useState('executive')

  const heatmapPillars = ['scientific_rd', 'math_proofs', 'software_systems'].map((key) => ({
    key,
    accent: PILLAR_META[key].accent,
    shortLabel: PILLAR_META[key].shortLabel,
    unit: PILLAR_META[key].unit
  }))

  const breakthroughByPillar = (key) => latest?.top_signals?.find((b) => b.pillar === key)
  const pillarSignals = (key) => latest?.top_signals?.filter((b) => b.pillar === key) || []

  // Check if we are in a specific pillar tab
  const activePillarData = activeTab !== 'executive' && latest?.pillars?.[activeTab] ? latest.pillars[activeTab] : null

  return (
    <div className={`min-h-screen bg-graphite-950 bg-grid ${isArabic ? "font-['Thmanyah_Sans']" : ''}`} dir={dir}>
      <Header generatedAt={latest?.generated_at} isDemo={latest?.status === 'demo'} />

      {latest && (
        <nav className="border-b border-graphite-800 bg-graphite-950/80 backdrop-blur top-0 sticky z-40 overflow-x-auto hide-scrollbar">
          <div className="mx-auto flex max-w-6xl items-center gap-2 px-6">
            <button
              onClick={() => setActiveTab('executive')}
              className={`whitespace-nowrap border-b-2 px-4 py-3 font-mono text-[13px] transition-colors ${
                activeTab === 'executive'
                  ? 'border-signal-amber font-semibold text-signal-amber'
                  : 'border-transparent text-paper-500 hover:border-paper-600 hover:text-paper-300'
              }`}
            >
              {t('Forecast & Daily Life Impact')}
            </button>
            {Object.keys(PILLAR_META).map((key) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`whitespace-nowrap flex items-center gap-2 border-b-2 px-4 py-3 font-mono text-[13px] transition-colors ${
                  activeTab === key
                    ? 'font-semibold'
                    : 'border-transparent text-paper-500 hover:border-paper-600 hover:text-paper-300'
                }`}
                style={activeTab === key ? { borderColor: PILLAR_META[key].accent, color: PILLAR_META[key].accent } : {}}
              >
                {t(PILLAR_META[key].shortLabel)}
              </button>
            ))}
          </div>
        </nav>
      )}

      <main className="mx-auto max-w-6xl px-6 py-8">
        {latestLoading && <p className="text-sm font-mono text-paper-500">Loading latest signals…</p>}

        {latestError && (
          <div className="border border-signal-rose/40 bg-signal-rose/5 px-5 py-4 text-sm text-signal-rose">
            Couldn't load <code className="font-mono">data/latest_data.json</code>. If you're running this outside{' '}
            <code className="font-mono">npm run dev</code>, make sure the file exists at{' '}
            <code className="font-mono">public/data/latest_data.json</code>.
          </div>
        )}

        {latest && activeTab === 'executive' && (
          <div className="flex flex-col gap-10">
            {/* Executive Intelligence Overview */}
            <section className="flex flex-col gap-5">
              <SectionHeader icon={Activity} title="Executive Intelligence Overview" badge="BI Protocol v2.0" />
              <ExecutiveCommandCenter
                decision={latest.executive_decision}
                protocol={latest.protocol}
                kpis={latest.kpis}
              />
              <CompositeIndex
                composite={latest.composite_index}
                kpis={latest.kpis}
              />
            </section>

            {/* Strategic Forecast Matrix */}
            {latest.strategic_forecast && (
              <section className="flex flex-col gap-5">
                <SectionHeader icon={Target} title="Strategic Forecast Horizon" badge="Projections" />
                <ForecastMatrix forecast={latest.strategic_forecast} />
              </section>
            )}

            {/* Capability Pillars Grid - Used as Quick Links from Executive View */}
            <section className="flex flex-col gap-5">
              <SectionHeader icon={Layers} title="Pillar Capability Matrix" badge="0–100 Scores" />
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {Object.entries(latest.pillars).map(([key, pillar]) => (
                  <div key={key} onClick={() => setActiveTab(key)} className="cursor-pointer group hover:scale-[1.01] transition-transform">
                    <CapabilityCard
                      icon={PILLAR_META[key]?.icon ?? Compass}
                      accent={PILLAR_META[key]?.accent ?? '#C7C2B8'}
                      pillar={pillar.name}
                      score={pillar.score}
                      deltaToday={pillar.delta_today}
                      delta7d={pillar.delta_7d}
                      summary={key === 'software_systems' ? 'Monitor systems that can code...' : 'Focus here on...'}
                      breakthrough={breakthroughByPillar(key)}
                    />
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {latest && activePillarData && (
          <div className="flex flex-col gap-10">
            <section className="flex flex-col gap-5">
              <SectionHeader icon={PILLAR_META[activeTab].icon} title={activePillarData.name} badge="Pillar Deep Dive" />
              <div className="grid gap-6 md:grid-cols-2">
                <CapabilityCard
                  icon={PILLAR_META[activeTab].icon}
                  accent={PILLAR_META[activeTab].accent}
                  pillar={activePillarData.name}
                  score={activePillarData.score}
                  deltaToday={activePillarData.delta_today}
                  delta7d={activePillarData.delta_7d}
                />
                
                {/* Visual Analytics space dedicated for this pillar */}
                {trends?.days && (
                  <div className="flex h-full flex-col justify-center border border-graphite-600 bg-graphite-900/60 p-5">
                    <h4 className="font-mono text-[11px] text-paper-500 uppercase tracking-widest">{t('Historical Momentum')}</h4>
                    <div className="mt-4 flex-1 min-h-[140px]">
                       {/* Filtering the charts to only show active pillar */}
                       <HeatmapWidget
                          history={trends.days}
                          pillars={[heatmapPillars.find(p => p.key === activeTab)]}
                          activePillar={activeTab}
                       />
                    </div>
                  </div>
                )}
              </div>
            </section>

            <section className="flex flex-col gap-5">
              <SectionHeader icon={ShieldCheck} title={`Signals for ${activePillarData.name}`} badge={`${pillarSignals(activeTab).length} Signals`} />
              <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
                {pillarSignals(activeTab).length > 0 ? (
                  <SignalFeed
                    items={pillarSignals(activeTab)}
                    pillarAccents={{ [activeTab]: PILLAR_META[activeTab].accent }}
                  />
                ) : (
                  <div className="border border-graphite-700 bg-graphite-900/40 p-8 flex flex-col items-center justify-center text-center">
                    <CircleDashed size={32} className="text-paper-600 mb-4" />
                    <p className="font-mono text-sm text-paper-400">{t('No new critical signals detected for this pillar today.')}</p>
                  </div>
                )}
                
                <VerifyPalette />
              </div>
            </section>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
