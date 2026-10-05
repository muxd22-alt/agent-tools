import { useI18n } from '../i18n.jsx'

export default function Footer() {
  const { t } = useI18n()

  return (
    <footer className="border-t border-graphite-700">
      <div className="mx-auto max-w-6xl px-6 py-8 text-xs text-paper-500">
        <p className="leading-relaxed">
          {t('Data sources: GitHub REST API, Hugging Face Daily Papers, and the arXiv API. Every score and breakthrough on this page links back to a primary source — treat unlinked claims as unverified.')}
          {' '}
          <span className="text-paper-400">
            Rebuilt daily by <code className="font-mono text-paper-300">.github/workflows/daily-update.yml</code>.
          </span>
        </p>
        <p className="mt-3">
          {t('This project tracks public research signals as an indicator of momentum, not a prediction of if or when AGI arrives. Scores are heuristic and intentionally legible about their own uncertainty.')}
        </p>
      </div>
    </footer>
  )
}
