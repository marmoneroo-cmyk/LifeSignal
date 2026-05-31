// UI translation strings. Keys are dot-namespaced by surface.
// Engine-generated medical findings come from the backend (English); the
// Narrative + Copilot surfaces already localize via the backend `lang` param.

export type Lang = "he" | "en";

type Entry = { he: string; en: string };

export const translations: Record<string, Entry> = {
  // --- App / nav ---
  "app.name": { he: "LifeSignal", en: "LifeSignal" },
  "sidebar.disclaimer": {
    he: "תמיכה בהחלטות בלבד — אינה אבחנה רפואית.",
    en: "Decision support only — not a medical diagnosis.",
  },
  "nav.dashboard": { he: "לוח בקרה", en: "Dashboard" },
  "nav.report": { he: "דוח בריאות", en: "Health Report" },
  "nav.copilot": { he: "קופיילוט רפואי", en: "Medical Copilot" },
  "nav.chat": { he: "שאל את LifeSignal", en: "Ask LifeSignal" },
  "nav.timeline": { he: "ציר זמן", en: "Timeline" },
  "nav.upload": { he: "העלאת PDF", en: "Upload PDF" },
  "nav.labs": { he: "הוספת בדיקות דם", en: "Add Lab Results" },
  "nav.insurance": { he: "הוספת ביטוח", en: "Add Insurance" },
  "nav.medications": { he: "תרופות", en: "Medications" },
  "nav.family": { he: "היסטוריה משפחתית", en: "Family History" },
  "nav.goals": { he: "מטרות בריאות", en: "Health Goals" },
  "nav.share": { he: "שיתוף עם רופא", en: "Share with Doctor" },

  // --- Common ---
  "common.logout": { he: "התנתקות", en: "Log out" },
  "common.cancel": { he: "ביטול", en: "Cancel" },
  "common.add": { he: "הוספה", en: "Add" },
  "common.save": { he: "שמירה", en: "Save" },
  "common.loading": { he: "טוען…", en: "Loading…" },
  "common.nothingFlagged": { he: "לא סומן דבר.", en: "Nothing flagged." },
  "common.noProfile": { he: "אין פרופיל פעיל.", en: "No active profile." },
  "common.apiError": { he: "לא ניתן להתחבר לשרת.", en: "Could not reach the API." },
  "common.language": { he: "שפה", en: "Language" },

  // --- Auth / profiles ---
  "auth.login": { he: "התחברות", en: "Log in" },
  "auth.register": { he: "הרשמה", en: "Register" },
  "auth.fullName": { he: "שם מלא", en: "Full name" },
  "auth.email": { he: "אימייל", en: "Email" },
  "auth.password": { he: "סיסמה", en: "Password" },
  "auth.create": { he: "צור חשבון", en: "Create account" },
  "auth.pleaseWait": { he: "רגע…", en: "Please wait…" },
  "auth.demoHint": { he: "הדגמה: demo@demo.com / demo1234", en: "Demo: demo@demo.com / demo1234" },
  "auth.error": { he: "משהו השתבש.", en: "Something went wrong." },
  "auth.guidelines": { he: "הנחיות:", en: "Guidelines:" },
  "profile.add": { he: "הוספת פרופיל משפחתי", en: "Add family profile" },
  "profile.addTitle": { he: "הוספת פרופיל משפחתי", en: "Add a family profile" },
  "profile.account": { he: "חשבון", en: "account" },
  "profile.namePlaceholder": { he: "שם (למשל ילד/ה)", en: "Name (e.g. child)" },

  // --- Enums ---
  "sex.male": { he: "זכר", en: "Male" },
  "sex.female": { he: "נקבה", en: "Female" },
  "region.intl": { he: "בינלאומי", en: "International" },
  "region.il": { he: "ישראל (משרד הבריאות)", en: "Israel (MoH)" },
  "region.us": { he: "ארה״ב (USPSTF)", en: "USPSTF (US)" },
  "region.eu": { he: "אירופה", en: "European" },
  "priority.critical": { he: "קריטי", en: "Critical" },
  "priority.high": { he: "גבוה", en: "High" },
  "priority.preventive": { he: "מניעתי", en: "Preventive" },
  "priority.informational": { he: "מידע", en: "Info" },
  "status.normal": { he: "תקין", en: "normal" },
  "status.borderline": { he: "גבולי", en: "borderline" },
  "status.abnormal": { he: "חריג", en: "abnormal" },
  "dir.rising": { he: "עולה", en: "rising" },
  "dir.falling": { he: "יורד", en: "falling" },
  "dir.stable": { he: "יציב", en: "stable" },

  // --- Dashboard ---
  "dash.hello": { he: "שלום, {name}", en: "Hello, {name}" },
  "dash.subtitle": { he: "{sex}, גיל {age}. הנה מה שהנתונים שלך מספרים.", en: "{sex}, age {age}. Here is what your data is telling you." },
  "dash.healthScore": { he: "ציון בריאות", en: "Health Score" },
  "dash.scoreFooter": { he: "אות מורכב על פני {n} תחומים שנמדדו", en: "Composite signal across {n} measured domains" },
  "dash.topThree": { he: "3 הדברים החשובים ביותר כעת", en: "3 most important things right now" },
  "dash.nothingUrgent": { he: "אין דבר דחוף. המשך בהרגלים המונעים.", en: "Nothing urgent. Keep up the preventive habits." },
  "dash.missingScreenings": { he: "בדיקות מומלצות", en: "Missing screenings" },
  "dash.insuranceInsights": { he: "תובנות ביטוח", en: "Insurance insights" },
  "dash.reminders": { he: "תזכורות והתראות", en: "Reminders & alerts" },
  "dash.noReminders": { he: "אין תזכורות פעילות.", en: "No active reminders." },
  "dash.emergencyTitle": { he: "מומלצת בדיקה רפואית בהקדם", en: "Prompt medical evaluation recommended" },
  "dash.loading": { he: "טוען את האינטליגנציה הרפואית שלך…", en: "Loading your health intelligence…" },
  "dash.more": { he: "+{n} נוספים ←", en: "+{n} more →" },

  // --- Report ---
  "report.title": { he: "דוח בריאות מנהלים", en: "Executive Health Report" },
  "report.building": { he: "בונה את הדוח שלך…", en: "Building your report…" },
  "report.print": { he: "הדפסה / PDF", en: "Print / PDF" },
  "report.export": { he: "ייצוא", en: "Export" },
  "report.scoreByDomain": { he: "ציון בריאות לפי תחום", en: "Health score by domain" },
  "report.labMarkers": { he: "מרקרים ומגמות מעבדה", en: "Lab markers & trends" },
  "report.noLabData": { he: "אין נתוני מעבדה — הוסף תוצאות כדי לראות מגמות.", en: "No lab data yet — add results to see trends." },
  "report.latest": { he: "אחרון", en: "latest" },
  "report.howCompare": { he: "איך אתה ביחס לאוכלוסייה (אחוזון)", en: "How you compare (percentile vs. population)" },
  "report.percentile": { he: "אחוזון", en: "pct" },
  "report.percentileNote": { he: "אחוזון = היכן הערך האחרון שלך ביחס לאוכלוסייה בוגרת מקורבת.", en: "Percentile = where your latest value sits vs. an approximate adult population." },
  "report.yearOverYear": { he: "השוואה שנה-מול-שנה", en: "Year-over-year comparison" },
  "report.noData": { he: "אין מספיק נתונים.", en: "Not enough data." },
  "section.urgent": { he: "התראות דחופות", en: "Urgent alerts" },
  "section.risks": { he: "סיכונים וממצאים", en: "Risks & findings" },
  "section.projections": { he: "תחזיות עתידיות", en: "Future projections" },
  "section.secondOpinion": { he: "חוות דעת שנייה — כדאי לברר", en: "Second opinion — worth exploring" },
  "section.drugs": { he: "אינטראקציות תרופתיות", en: "Medication interactions" },
  "section.family": { he: "היסטוריה משפחתית וסיכון תורשתי", en: "Family history & hereditary risk" },
  "section.screenings": { he: "בדיקות מונעות מומלצות", en: "Recommended preventive screenings" },
  "section.insurance": { he: "ייעול ביטוחי", en: "Insurance optimization" },
  "section.negotiator": { he: "ניתוח כדאיות ביטוח", en: "Insurance negotiator — value review" },
  "section.claims": { he: "תביעות אפשריות", en: "Possible claims" },
  "section.coverage": { he: "כיסוי לבדיקות מומלצות", en: "Coverage for recommended tests" },

  // --- Narrative card ---
  "narr.title": { he: "סיכום בריאות חכם", en: "AI Health Summary" },
  "narr.generate": { he: "צור סיכום בשפה פשוטה", en: "Generate plain-language summary" },
  "narr.writing": { he: "כותב את הסיכום שלך…", en: "Writing your summary…" },
  "narr.sourceAi": { he: "נוצר ע״י AI ({model})", en: "AI-generated ({model})" },
  "narr.sourceRule": { he: "סיכום מבוסס-כללים (הגדר ANTHROPIC_API_KEY ל-AI)", en: "Rule-based summary (set ANTHROPIC_API_KEY for AI narration)" },

  // --- Copilot ---
  "copilot.title": { he: "קופיילוט רפואי", en: "Medical Copilot" },
  "copilot.subtitle": { he: "התכונן לביקור הבא אצל הרופא.", en: "Prepare for your next doctor visit." },
  "copilot.prepare": { he: "הכן את הביקור שלי", en: "Prepare my visit" },
  "copilot.preparing": { he: "מכין…", en: "Preparing…" },
  "copilot.questions": { he: "שאלות לשאול", en: "Questions to ask" },
  "copilot.changes": { he: "מה השתנה", en: "What changed" },

  // --- Timeline ---
  "timeline.title": { he: "ציר זמן רפואי אישי", en: "Personal Medical Timeline" },
  "timeline.subtitle": { he: "הזיכרון הבריאותי שלך לאורך זמן, מהחדש לישן.", en: "Your longitudinal health memory, newest first." },
  "timeline.events": { he: "אירועים", en: "Events" },
  "timeline.noEvents": { he: "אין אירועים עדיין.", en: "No events yet." },

  // --- Forms: labs ---
  "labs.title": { he: "הוספת תוצאות בדיקה", en: "Add Lab Results" },
  "labs.subtitle": { he: "הזן ערכי בדיקת דם. המנוע מזהה חריגות ומגמות לאורך זמן.", en: "Enter blood-test values. The engine detects abnormalities and trends over time." },
  "labs.new": { he: "תוצאות חדשות", en: "New results" },
  "labs.marker": { he: "מרקר", en: "Marker" },
  "labs.value": { he: "ערך", en: "Value" },
  "labs.date": { he: "תאריך", en: "Date" },
  "labs.addAnother": { he: "הוסף מרקר נוסף", en: "Add another marker" },
  "labs.save": { he: "שמור תוצאות", en: "Save results" },
  "labs.enterValue": { he: "הזן לפחות ערך אחד.", en: "Enter at least one value." },
  "labs.saved": { he: "נשמרו {n} תוצאות. פתח את לוח הבקרה לראות את הניתוח המעודכן.", en: "Saved {n} result(s). Open the Dashboard to see the updated analysis." },
  "labs.failed": { he: "השמירה נכשלה.", en: "Failed to save." },

  // --- Forms: insurance ---
  "ins.title": { he: "הוספת פוליסות ביטוח", en: "Add Insurance Policies" },
  "ins.subtitle": { he: "המנתח מזהה כפילויות, חוסר בכיסוי קריטי והתאמה לגיל.", en: "The analyzer flags duplicates, missing critical cover, and age-relevance." },
  "ins.policies": { he: "פוליסות", en: "Policies" },
  "ins.provider": { he: "חברה", en: "Provider" },
  "ins.coverage": { he: "כיסוי", en: "Coverage" },
  "ins.perMonth": { he: "₪/חודש", en: "$/month" },
  "ins.renewal": { he: "חידוש", en: "Renewal" },
  "ins.addAnother": { he: "הוסף פוליסה נוספת", en: "Add another policy" },
  "ins.save": { he: "שמור פוליסות", en: "Save policies" },
  "ins.needOne": { he: "הוסף לפחות פוליסה אחת עם שם חברה.", en: "Add at least one policy with a provider name." },
  "ins.saved": { he: "נשמרו {n} פוליסות. פתח את לוח הבקרה לתובנות ביטוח.", en: "Saved {n} polic(ies). Open the Dashboard to see insurance insights." },

  // --- Forms: medications ---
  "med.title": { he: "תרופות", en: "Medications" },
  "med.subtitle": { he: "אנו בודקים אינטראקציות וכפילות. זו אינה המלצה רפואית — אמת מול רוקח.", en: "We check for interactions and duplicate-class therapy. This is not medical advice — confirm with a pharmacist." },
  "med.your": { he: "התרופות שלך", en: "Your medications" },
  "med.medication": { he: "תרופה", en: "Medication" },
  "med.dose": { he: "מינון (לא חובה)", en: "Dose (optional)" },
  "med.addAnother": { he: "הוסף תרופה נוספת", en: "Add another medication" },
  "med.save": { he: "שמור תרופות", en: "Save medications" },
  "med.needOne": { he: "הוסף לפחות תרופה אחת.", en: "Add at least one medication." },
  "med.saved": { he: "נשמרו {n} תרופות. פתח את לוח הבקרה לבדיקת אינטראקציות.", en: "Saved {n} medication(s). Open the Dashboard to see interaction checks." },

  // --- Forms: family ---
  "fam.title": { he: "גרף בריאות משפחתי", en: "Family Health Graph" },
  "fam.subtitle": { he: "מצבי קרובי משפחה עוזרים לזהות סיכון תורשתי ולהקדים בדיקות רלוונטיות.", en: "Relatives' conditions help spot hereditary risk and bring relevant screenings earlier." },
  "fam.relatives": { he: "קרובי משפחה", en: "Relatives" },
  "fam.relation": { he: "קרבה", en: "Relation" },
  "fam.addAnother": { he: "הוסף קרוב נוסף", en: "Add another relative" },
  "fam.save": { he: "שמור היסטוריה משפחתית", en: "Save family history" },
  "fam.needOne": { he: "הוסף לפחות קרוב אחד עם מצב רפואי.", en: "Add at least one relative with a condition." },
  "fam.saved": { he: "נשמרו {n} קרובים. הסיכון התורשתי מוזן כעת להמלצות הבדיקה.", en: "Saved {n} relative(s). Hereditary risk now feeds your screening recommendations." },

  // relations
  "rel.father": { he: "אב", en: "father" },
  "rel.mother": { he: "אם", en: "mother" },
  "rel.sibling": { he: "אח/ות", en: "sibling" },
  "rel.grandparent": { he: "סב/תא", en: "grandparent" },
  "rel.child": { he: "ילד/ה", en: "child" },
  "rel.aunt": { he: "דודה", en: "aunt" },
  "rel.uncle": { he: "דוד", en: "uncle" },
  // conditions
  "cond.heart_disease": { he: "מחלת לב", en: "heart disease" },
  "cond.diabetes": { he: "סוכרת", en: "diabetes" },
  "cond.breast_cancer": { he: "סרטן שד", en: "breast cancer" },
  "cond.ovarian_cancer": { he: "סרטן שחלות", en: "ovarian cancer" },
  "cond.colon_cancer": { he: "סרטן מעי", en: "colon cancer" },
  "cond.prostate_cancer": { he: "סרטן ערמונית", en: "prostate cancer" },
  "cond.melanoma": { he: "מלנומה", en: "melanoma" },

  // --- Upload ---
  "up.title": { he: "העלאת מסמך", en: "Upload a Document" },
  "up.subtitle": { he: "העלה PDF של בדיקת דם או ביטוח. נחלץ את הערכים לבדיקתך לפני שמירה.", en: "Upload a blood-test or insurance PDF. We extract the values for you to review before saving." },
  "up.choose": { he: "בחר PDF", en: "Choose a PDF" },
  "up.docType": { he: "סוג מסמך", en: "Document type" },
  "up.auto": { he: "זיהוי אוטומטי", en: "Auto-detect" },
  "up.lab": { he: "בדיקת דם", en: "Blood test" },
  "up.insurance": { he: "פוליסת ביטוח", en: "Insurance policy" },
  "up.reading": { he: "קורא PDF…", en: "Reading PDF…" },
  "up.clickSelect": { he: "לחץ לבחירת PDF", en: "Click to select a PDF" },
  "up.hint": { he: "PDF עם שכבת טקסט · עד 10MB · ניתן לבחור כמה", en: "Text-layer PDFs · max 10 MB · multiple allowed" },
  "up.review": { he: "סקירת הנתונים שחולצו", en: "Review extracted data" },
  "up.labResults": { he: "תוצאות מעבדה ({n})", en: "Lab results ({n})" },
  "up.policiesFound": { he: "פוליסות ביטוח ({n})", en: "Insurance policies ({n})" },
  "up.confirmSave": { he: "אישור ושמירה", en: "Confirm & save" },
  "up.fromLine": { he: "מתוך השורה", en: "From line" },
  "up.processed": { he: "עובדו {n} קבצים.", en: "Processed {n} files." },
  "up.disclaimer": { he: "החילוץ הוא מיטבי מטקסט המסמך. תמיד אמת מול הדוח המקורי לפני הסתמכות.", en: "Extraction is best-effort from the document text. Always verify values against your original report before relying on them." },
};

export function translate(lang: Lang, key: string, vars?: Record<string, string | number>): string {
  const entry = translations[key];
  let text = entry ? entry[lang] : key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      text = text.replace(`{${k}}`, String(v));
    }
  }
  return text;
}
