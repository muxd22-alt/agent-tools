import { createContext, useContext, useState, useCallback, useMemo } from 'react'

const I18nContext = createContext()

// Static Arabic translations for all fixed UI strings.
// The scraper's dynamic content (summaries, breakthroughs) is translated on-demand via API.
const AR = {
  // Header
  'AGI Horizon Tracker': 'مُتتبّع أُفق الذكاء الاصطناعي العام',
  'Source-grounded signals across three frontier capability pillars': 'إشارات مُوثّقة المصدر عبر ثلاثة محاور قدرات رائدة',
  'Demo data': 'بيانات تجريبية',
  'Updated': 'آخر تحديث',

  // Composite Index
  'Composite horizon index': 'مؤشر الأُفق المُركّب',
  'this week': 'هذا الأسبوع',

  // Pillar names
  'Autonomous Scientific R&D': 'البحث والتطوير العلمي المُستقل',
  'Formal Mathematical Proofs': 'البراهين الرياضية الرسمية',
  'Vast Software Systems': 'أنظمة برمجية واسعة',
  'Forecast & Daily Life Impact': 'التوقعات وتأثيرها على الحياة اليومية',

  // Card labels
  'Latest signal': 'أحدث إشارة',
  'Verified': 'تم التحقق',
  'Pending review': 'قيد المراجعة',
  'Impact on everyday life': 'تأثيرها على الحياة اليومية',
  '7-day trend': 'اتجاه ٧ أيام',

  // Signal Feed
  'Daily signals': 'الإشارات اليومية',
  'Every item links to its primary source. Nothing here is taken on faith.': 'كل عنصر مربوط بمصدره الأصلي. لا شيء هنا يُؤخذ على الثقة.',
  'Human impact': 'الأثر البشري',
  'How to verify': 'كيف تتحقق',
  'Scientific R&D': 'البحث والتطوير العلمي',
  'Math Proofs': 'البراهين الرياضية',
  'Software Systems': 'الأنظمة البرمجية',

  // Forecast Matrix
  'Forecast matrix': 'مصفوفة التوقعات',
  'Projected, not measured — extrapolated from the momentum above.': 'توقعات وليست قياسات — مُستنتجة من الزخم أعلاه.',
  '30 days': '٣٠ يوماً',
  '90 days': '٩٠ يوماً',
  '365 days': '٣٦٥ يوماً',
  'Low': 'منخفض',
  'Medium': 'متوسط',
  'High': 'مرتفع',
  'Critical': 'حرج',

  // Verify Palette
  'Verification command palette': 'لوحة أوامر التحقق',
  'Copy, paste, and check the sources yourself.': 'انسخ والصق وتحقق من المصادر بنفسك.',
  'Copy': 'نسخ',
  'Copied': 'تم النسخ',
  'Build a Lean 4 / Mathlib proof locally': 'بناء برهان Lean 4 / Mathlib محلياً',
  "Pull an arXiv paper's raw metadata": 'سحب بيانات ورقة arXiv الخام',
  // Executive Summary & BI Badges
  'Executive Summary': 'الملخص التنفيذي',
  'Curation Protocol': 'بروتوكول التنسيق',
  'Executive Intelligence Overview': 'نظرة عامة على الذكاء التنفيذي',
  'Pillar Capability Matrix': 'مصفوفة قدرات المحاور الرئيسيّة',
  'Momentum & 90-Day Trajectory': 'الزخم ومسار الـ ٩٠ يوماً',
  'Strategic Forecast Horizon': 'أُفق التوقعات الاستراتيجية',
  'Empirical Evidence & Verification Engine': 'محرّك الأدلة التجريبية والتحقق',
  
  // Executive Engine
  'Market / Intelligence Regime': 'حالة الاستخبارات والسوق',
  'Signal Velocity': 'سرعة الإشارات',
  'Leading Pillar': 'المحور المتصدر',
  'Confidence': 'درجة الثقة',
  'Strategic Bias': 'التحيز الاستراتيجي',
  'Executive Brief': 'الموجز التنفيذي',
  'Data Product Quality KPIs': 'مؤشرات أداء جودة البيانات',

  // KPIs
  'Signal Coverage': 'تغطية الإشارات',
  'Source Diversity': 'تنوع المصادر',
  'Evidence Freshness': 'حداثة الأدلة',
  'Duplicate Rate': 'معدل التكرار',
  'AI Agreement': 'توافق الذكاء الاصطناعي',

  // Signal Objects
  'Signal Score': 'تقييم الإشارة',
  'Novelty': 'الحداثة',
  'Quality': 'الجودة',
  'Importance': 'الأهمية',
  'Supporting Evidence': 'الأدلة الداعمة',
  'Contradicting Evidence': 'الأدلة المضادة',
  'Why It Matters': 'لماذا يهم؟',
  'Recommended Action': 'الإجراء الموصى به',
  'Partial': 'جزئي',
  'Unverified Claim': 'ادعاء لم يُتحقق منه',

  // Footer
  'Data sources: GitHub REST API, Hugging Face Daily Papers, and the arXiv API. Every score and breakthrough on this page links back to a primary source — treat unlinked claims as unverified.': 'مصادر البيانات: واجهة GitHub، أوراق Hugging Face اليومية، وواجهة arXiv. كل درجة واكتشاف في هذه الصفحة مرتبط بمصدره الأصلي.',
  'This project tracks public research signals as an indicator of momentum, not a prediction of if or when AGI arrives. Scores are heuristic and intentionally legible about their own uncertainty.': 'يتتبع هذا المشروع الإشارات البحثية العامة كمؤشر للزخم، وليس كتنبؤ بموعد وصول الذكاء الاصطناعي العام. الدرجات استدلالية وشفافة بشأن حالة عدم اليقين.',

  // General
  'Unweighted average of the three tracked pillars below, each scored 0–100 against its own historical baseline. A heuristic momentum gauge, not a forecast of arrival.': 'المتوسط غير المرجح للمحاور الثلاثة المرصودة أدناه، حيث تسجل كل منها درجة من ٠ إلى ١٠٠ مقارنة بخط الأساس التاريخي الخاص بها. مقياس زخم استدلالي، وليس تنبؤاً بالوصول.',
  'Working Code Repo': 'مستودع كود عامل',
}

// MyMemory free translation API for dynamic scraper-generated content
const translationCache = {}
async function translateText(text) {
  if (!text || text.length < 3) return text
  if (translationCache[text]) return translationCache[text]
  try {
    const res = await fetch(
      `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text.slice(0, 500))}&langpair=en|ar`
    )
    const data = await res.json()
    const translated = data?.responseData?.translatedText
    if (translated && !translated.toUpperCase().includes('MYMEMORY WARNING')) {
      translationCache[text] = translated
      return translated
    }
  } catch (e) {
    console.warn('[i18n] translation API error:', e)
  }
  return text
}

export function I18nProvider({ children }) {
  const [lang, setLang] = useState(() => {
    try { return localStorage.getItem('agi_lang') || 'en' } catch { return 'en' }
  })

  const toggleLang = useCallback(() => {
    const next = lang === 'en' ? 'ar' : 'en'
    setLang(next)
    try { localStorage.setItem('agi_lang', next) } catch {}
  }, [lang])

  const t = useCallback((key) => {
    if (lang === 'en') return key
    return AR[key] ?? key
  }, [lang])

  const value = useMemo(() => ({
    lang,
    isArabic: lang === 'ar',
    dir: lang === 'ar' ? 'rtl' : 'ltr',
    toggleLang,
    t,
    translateDynamic: lang === 'ar' ? translateText : (text) => Promise.resolve(text),
  }), [lang, toggleLang, t])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  return useContext(I18nContext)
}
