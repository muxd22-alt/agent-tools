import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { useI18n } from '../i18n.jsx'

const COMMANDS = [
  {
    label: 'Build a Lean 4 / Mathlib proof locally',
    snippet: 'git clone --depth 1 https://github.com/leanprover-community/mathlib4.git\ncd mathlib4 && lake build'
  },
  {
    label: "Pull an arXiv paper's raw metadata",
    snippet: 'curl -s "http://export.arxiv.org/api/query?id_list=<ARXIV_ID>"'
  },
  {
    label: "Check a repo's recent commit activity",
    snippet: 'curl -s "https://api.github.com/repos/<OWNER>/<REPO>/commits?per_page=5"'
  },
  {
    label: 'Run the SWE-bench evaluation harness',
    snippet: 'git clone https://github.com/princeton-nlp/SWE-bench.git\ncd SWE-bench && pip install -e .'
  }
]

function CommandRow({ label, snippet }) {
  const { t } = useI18n()
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(snippet)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      // Clipboard API unavailable
    }
  }

  return (
    <div className="border border-graphite-700 bg-graphite-950/60">
      <div className="flex items-center justify-between border-b border-graphite-700 px-3.5 py-2">
        <span className="text-xs text-paper-300">{t(label)}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 border border-graphite-600 px-2 py-1 font-mono text-[10px] text-paper-500 transition-colors hover:border-signal-cyan/50 hover:text-signal-cyan"
        >
          {copied ? <Check size={11} /> : <Copy size={11} />}
          {copied ? t('Copied') : t('Copy')}
        </button>
      </div>
      <pre className="overflow-x-auto px-3.5 py-3 font-mono text-xs leading-relaxed text-signal-cyan/90" dir="ltr">{snippet}</pre>
    </div>
  )
}

export default function VerifyPalette() {
  const { t } = useI18n()

  return (
    <div className="border border-graphite-600 bg-graphite-900/60">
      <header className="border-b border-graphite-700 px-5 py-4">
        <h3 className="text-sm font-medium text-paper-100">{t('Verification command palette')}</h3>
        <p className="mt-0.5 text-xs text-paper-500">{t('Copy, paste, and check the sources yourself.')}</p>
      </header>
      <div className="grid gap-3 px-5 py-5 sm:grid-cols-2">
        {COMMANDS.map((cmd) => (
          <CommandRow key={cmd.label} {...cmd} />
        ))}
      </div>
    </div>
  )
}
