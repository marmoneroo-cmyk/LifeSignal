"""Hebrew translation layer for engine-generated findings.

Engines emit English findings (titles, details, plain_language) built from
deterministic templates. This module translates them to Hebrew by:
  1) Replacing marker labels (e.g. "LDL cholesterol" → "כולסטרול LDL")
  2) Pattern-matching the templated sentences and producing Hebrew equivalents

The translation is idempotent — if no pattern matches, the original text is
returned. This guarantees no information is lost; in the worst case we degrade
to English (which is what the user sees today).
"""
from __future__ import annotations

import re

from app.schemas import Finding, HealthReport, MarkerTrend, ScoreComponent

# ---- Marker labels --------------------------------------------------------

MARKER_LABELS_HE: dict[str, str] = {
    "LDL cholesterol":              "כולסטרול LDL (רע)",
    "HDL cholesterol":              "כולסטרול HDL (טוב)",
    "Triglycerides":                "טריגליצרידים",
    "Total cholesterol":            "כולסטרול כללי",
    "Fasting glucose":              "גלוקוז בצום",
    "HbA1c":                        "HbA1c (סוכר ממוצע)",
    "Hemoglobin":                   "המוגלובין",
    "Ferritin (iron stores)":       "פריטין (אחסון ברזל)",
    "Serum iron":                   "ברזל בסרום",
    "TSH (thyroid)":                "TSH (בלוטת התריס)",
    "Creatinine (kidney)":          "קריאטינין (כליות)",
    "eGFR (kidney function)":       "eGFR (תפקוד כליות)",
    "Uric acid":                    "חומצה אורית",
    "Sodium":                       "נתרן",
    "Potassium":                    "אשלגן",
    "Calcium":                      "סידן",
    "ALT (liver)":                  "ALT (כבד)",
    "AST (liver)":                  "AST (כבד)",
    "GGT (liver)":                  "GGT (כבד)",
    "Total bilirubin":              "בילירובין",
    "Albumin":                      "אלבומין",
    "CRP (inflammation)":           "CRP (דלקת)",
    "Vitamin D (25-OH)":            "ויטמין D",
    "Vitamin B12":                  "ויטמין B12",
    "Folate":                       "חומצה פולית",
    "PSA (prostate)":               "PSA (ערמונית)",
    "Systolic blood pressure":      "לחץ דם סיסטולי",
    "Diastolic blood pressure":     "לחץ דם דיאסטולי",
    "MCV (red cell size)":          "MCV (גודל כדורית אדומה)",
    "MCH":                          "MCH",
    "White blood cells":            "כדוריות דם לבנות",
    "Platelets":                    "טסיות דם",
}

# ---- Status / direction words --------------------------------------------

STATUS_HE = {"abnormal": "חריג", "borderline": "גבולי", "normal": "תקין"}
DIRECTION_HE = {"rising": "עולה", "falling": "יורד", "stable": "יציב"}

# ---- Domain labels (for ScoreComponent.domain) ---------------------------

DOMAIN_HE = {
    "Heart & vessels":       "לב וכלי דם",
    "Metabolism":            "מטבוליזם",
    "Blood":                 "דם",
    "Kidneys":               "כליות",
    "Liver":                 "כבד",
    "Cancer risk markers":   "סמני סיכון לסרטן",
    "Lifestyle":             "אורח חיים",
}

# ---- Coverage / insurance labels -----------------------------------------

COVERAGE_LABELS_HE: dict[str, str] = {
    "Basic health / ambulatory":                    "בריאות בסיסי / אמבולטורי",
    "Critical illness":                             "מחלות קשות",
    "Loss of working capacity (disability)":        "אובדן כושר עבודה",
    "Long-term care (nursing)":                     "סיעוד",
    "Medications outside the national basket":      "תרופות מחוץ לסל",
    "Private surgery / specialist":                 "ניתוחים פרטיים / יועץ",
    "Dental":                                       "טיפול שיניים",
    "Travel insurance":                             "ביטוח נסיעות",
}

# ---- Screening labels ----------------------------------------------------

SCREENING_HE: dict[str, str] = {
    "Colorectal cancer screening (colonoscopy / FIT)": "סקירה לסרטן מעי גס (קולונוסקופיה / FIT)",
    "Breast cancer screening (mammogram)":             "סקירה לסרטן שד (ממוגרפיה)",
    "BRCA genetic risk evaluation":                    "הערכת סיכון גנטי BRCA",
    "Cervical cancer screening (Pap / HPV)":           "סקירה לסרטן צוואר הרחם (פאפ / HPV)",
    "Prostate screening discussion (PSA)":             "שיחה על בדיקת ערמונית (PSA)",
    "Cholesterol / lipid panel":                       "בדיקת כולסטרול / שומנים",
    "Diabetes screening (HbA1c / fasting glucose)":    "סקירת סוכרת (HbA1c / גלוקוז)",
    "Blood pressure check":                            "מדידת לחץ דם",
    "Skin / mole examination":                         "בדיקת עור / שומות",
    "Abdominal aortic aneurysm ultrasound":            "אולטרסאונד אבי העורקים הבטני",
}

# ---- Drug labels (Title Case in titles) ----------------------------------

DRUG_HE: dict[str, str] = {
    "Warfarin": "וורפרין", "Aspirin": "אספירין", "Ibuprofen": "איבופרופן",
    "Atorvastatin": "אטורבסטטין", "Simvastatin": "סימבסטטין",
    "Metformin": "מטפורמין", "Lisinopril": "ליסינופריל",
    "Amlodipine": "אמלודיפין", "Omeprazole": "אומפרזול",
    "Clopidogrel": "קלופידוגרל", "Levothyroxine": "לבותירוקסין",
    "Ssri": "SSRI", "Vitamin K": "ויטמין K", "St Johns Wort": "פרע מחורר",
    "Grapefruit": "אשכולית", "Potassium Supplement": "תוסף אשלגן",
}

# ---- Title / detail / plain_language patterns ----------------------------
# Each entry: (regex, lambda groups → Hebrew). Order matters: more specific first.

def _label(name: str) -> str:
    return MARKER_LABELS_HE.get(name, name)


def _status(s: str) -> str:
    return STATUS_HE.get(s, s)


def _direction(d: str) -> str:
    return DIRECTION_HE.get(d, d)


def _coverage(name: str) -> str:
    return COVERAGE_LABELS_HE.get(name, name)


def _screening(name: str) -> str:
    return SCREENING_HE.get(name, name)


def _drug(name: str) -> str:
    return DRUG_HE.get(name, name)


# ---- Translation rules ----------------------------------------------------

def _t_title(s: str) -> str:
    # Blood: "LDL cholesterol: abnormal"
    m = re.match(r"^(.+?): (abnormal|borderline)$", s)
    if m:
        return f"{_label(m.group(1))}: {_status(m.group(2))}"
    # Blood: "LDL cholesterol: rising trend over 3 tests"
    m = re.match(r"^(.+?): (rising|falling|stable) trend over (\d+) tests$", s)
    if m:
        return f"{_label(m.group(1))}: מגמה {_direction(m.group(2))} לאורך {m.group(3)} בדיקות"
    # Screening: "Screening to verify: <name>"
    m = re.match(r"^Screening to verify: (.+)$", s)
    if m:
        return f"בדיקה מומלצת לאימות: {_screening(m.group(1))}"
    # Insurance
    m = re.match(r"^Duplicate coverage: (.+)$", s)
    if m:
        return f"כפילות בכיסוי: {_coverage(m.group(1))}"
    m = re.match(r"^Missing critical coverage: (.+)$", s)
    if m:
        return f"חסר כיסוי קריטי: {_coverage(m.group(1))}"
    m = re.match(r"^Renewal soon: (.+)$", s)
    if m:
        return f"חידוש בקרוב: {_coverage(m.group(1))}"
    m = re.match(r"^Age relevance: (.+)$", s)
    if m:
        return f"רלוונטיות לגיל: {_coverage(m.group(1))}"
    m = re.match(r"^High-cost line: (.+)$", s)
    if m:
        return f"פוליסה יקרה במיוחד: {_coverage(m.group(1))}"
    # Risk / projections
    if s == "Cardiovascular risk above average for your age":
        return "סיכון קרדיווסקולרי מעל הממוצע לגילך"
    if s == "Smoking raises multiple risks":
        return "עישון מעלה סיכונים בכמה תחומים"
    m = re.match(r"^Urgent: (.+)$", s)
    if m:
        return f"דחוף: {_translate_urgent(m.group(1))}"
    m = re.match(r"^Projection: (.+)$", s)
    if m:
        return f"תחזית: {_label(m.group(1))}"
    # Correlations
    if s == "Pattern: possible iron-deficiency anemia":
        return "תבנית: ייתכן חוסר ברזל / אנמיה"
    if s == "Pattern: metabolic / prediabetes signals":
        return "תבנית: סימני מטבוליזם / טרום-סוכרת"
    if s == "Pattern: liver enzymes elevated together":
        return "תבנית: אנזימי כבד מוגברים יחד"
    if s == "Pattern: reduced kidney function":
        return "תבנית: ירידה בתפקוד הכליות"
    # Drug interactions: "Interaction: Warfarin + Aspirin"
    m = re.match(r"^Interaction: (.+?) \+ (.+)$", s)
    if m:
        return f"אינטראקציה: {_drug(m.group(1))} + {_drug(m.group(2))}"
    m = re.match(r"^Possible duplicate therapy: (.+)$", s)
    if m:
        names = m.group(1).split(" + ")
        return "ייתכן טיפול כפול: " + " + ".join(_drug(n) for n in names)
    # Family
    m = re.match(r"^Family history: (.+)$", s)
    if m:
        cond = m.group(1)
        cond_he = {"heart disease": "מחלת לב", "diabetes": "סוכרת",
                   "breast cancer": "סרטן שד", "ovarian cancer": "סרטן שחלות",
                   "colon cancer": "סרטן מעי", "prostate cancer": "סרטן ערמונית",
                   "melanoma": "מלנומה"}.get(cond, cond)
        return f"היסטוריה משפחתית: {cond_he}"
    # Coverage matching
    m = re.match(r"^Coverage for: (.+)$", s)
    if m:
        return f"כיסוי עבור: {_screening(m.group(1))}"
    # Second opinion
    if s == "Worth exploring with your doctor":
        return "כדאי לבדוק עם הרופא"
    # Negotiator
    if s == "Consider expanding medication coverage":
        return "שקול הרחבת כיסוי תרופות"
    if s == "Re-evaluate critical-illness value":
        return "בחן מחדש את כדאיות ביטוח מחלות קשות"
    if s == "Long-term care gap":
        return "חסר כיסוי סיעודי"
    if s == "Review total insurance spend vs. risk":
        return "בחן את סך הוצאות הביטוח אל מול הסיכון"
    # Claims
    if s == "Possible claim: specialist / procedure cover":
        return "תביעה אפשרית: כיסוי יועץ / פרוצדורה"
    if s == "Possible claim: out-of-basket medications":
        return "תביעה אפשרית: תרופות מחוץ לסל"
    m = re.match(r"^Claimable under (.+)$", s)
    if m:
        return f"ניתן לתבוע תחת: {_coverage(m.group(1))}"
    return s


def _translate_urgent(s: str) -> str:
    mapping = {
        "Very high systolic blood pressure": "לחץ דם סיסטולי גבוה מאוד",
        "Very high diastolic blood pressure": "לחץ דם דיאסטולי גבוה מאוד",
        "Very high blood glucose": "רמת סוכר גבוהה מאוד בדם",
        "Very high potassium": "אשלגן גבוה מאוד",
        "Very low sodium": "נתרן נמוך מאוד",
        "Very low hemoglobin": "המוגלובין נמוך מאוד",
        "Very low kidney function (eGFR)": "תפקוד כליות נמוך מאוד (eGFR)",
        "Very low platelets": "טסיות נמוכות מאוד",
    }
    return mapping.get(s, s)


def _t_detail(s: str) -> str:
    # "Most recent value 162.0 mg/dL is abnormal for your profile."
    m = re.match(r"^Most recent value (.+?) (.+?) is (abnormal|borderline) for your profile\.$", s)
    if m:
        return f"הערך האחרון {m.group(1)} {m.group(2)} הוא {_status(m.group(3))} עבור הפרופיל שלך."
    # "LDL cholesterol has been rising across your last 3 results — a longitudinal pattern worth reviewing."
    m = re.match(r"^(.+?) has been (rising|falling|stable) across your last (\d+) results — a longitudinal pattern worth reviewing\.$", s)
    if m:
        return (
            f"{_label(m.group(1))} {_direction(m.group(2))} לאורך {m.group(3)} הבדיקות האחרונות — "
            "תבנית לאורך זמן שכדאי לבחון."
        )
    # Insurance details
    m = re.match(r"^You hold (\d+) overlapping (.+?) policies \((.+?)\), costing ~([\d.]+)/month combined\.$", s)
    if m:
        return (f"יש לך {m.group(1)} פוליסות חופפות של {_coverage(m.group(2))} ({m.group(3)}), "
                f"בעלות משולבת של כ-{m.group(4)} לחודש.")
    m = re.match(r"^No (.+?) policy was found in your uploaded coverage\.$", s)
    if m:
        return f"לא נמצאה פוליסת {_coverage(m.group(1))} בכיסוי שהעלית."
    m = re.match(r"^(.+?) is typically most relevant for ages (.+?); you are (\d+)\.$", s)
    if m:
        return f"{_coverage(m.group(1))} בדרך כלל רלוונטי לגילאי {m.group(2)}; אתה בן {m.group(3)}."
    m = re.match(r"^(.+?) renews in (\d+) days \((.+?)\)\.$", s)
    if m:
        return f"{_coverage(m.group(1))} מתחדש בעוד {m.group(2)} ימים ({m.group(3)})."
    # Drug
    if "Combined blood-thinning sharply raises bleeding risk" in s:
        return "שילוב מדללי דם מעלה משמעותית סיכון לדימום."
    if "NSAIDs with warfarin increase bleeding risk" in s:
        return "תרופות NSAID יחד עם וורפרין מעלות סיכון לדימום."
    if "may reduce clopidogrel effectiveness" in s:
        return "אומפרזול עלול להפחית את יעילות הקלופידוגרל."
    if "Dual antiplatelet therapy" in s:
        return "טיפול אנטי-טסיתי כפול מעלה סיכון לדימום; לעיתים מכוון אך דורש מעקב."
    if "increases GI bleeding risk" in s:
        return "השילוב מעלה סיכון לדימום במערכת העיכול."
    if "modestly increase bleeding risk" in s:
        return "השילוב מעלה במידה קלה סיכון לדימום."
    # Screening
    m = re.match(r"^Recommended for your profile \((.+?)\)\.(?: Elevated relevance due to family history: (.+?)\.)?$", s)
    if m:
        cadence = m.group(1)
        cadence_he = ("חד-פעמי" if cadence == "one-time"
                      else cadence.replace("every", "כל").replace("year(s)", "שנים"))
        out = f"מומלץ עבור הפרופיל שלך ({cadence_he})."
        if m.group(2):
            out += f" רלוונטיות מוגברת עקב היסטוריה משפחתית: {m.group(2)}."
        return out
    return s


def _t_plain(s: str) -> str:
    mapping = {
        "Your 'bad' cholesterol is a little above the ideal target.":
            "הכולסטרול ה'רע' שלך מעט מעל הטווח האידיאלי.",
        "Your 'bad' cholesterol is high enough to discuss with a doctor.":
            "הכולסטרול ה'רע' שלך גבוה מספיק כדי להתייעץ עם רופא.",
        "Your average blood sugar is starting to creep up.":
            "ממוצע הסוכר בדם שלך מתחיל לעלות.",
        "Your average blood sugar is in a range worth discussing with a doctor.":
            "ממוצע הסוכר בדם שלך בטווח שכדאי להתייעץ עליו עם רופא.",
        "Your red blood cell level is lower than expected, which can cause fatigue.":
            "רמת תאי הדם האדומים שלך נמוכה מהצפוי, מה שעלול לגרום לעייפות.",
        "Your iron stores look low.": "מאגרי הברזל שלך נראים נמוכים.",
        "Your vitamin D level is below the recommended range.":
            "רמת ויטמין D שלך נמוכה מהטווח המומלץ.",
        "Your thyroid hormone signal is outside the usual range.":
            "הורמון בלוטת התריס שלך מחוץ לטווח הרגיל.",
        "Stopping smoking is the single highest-impact change for your health score.":
            "הפסקת עישון היא השינוי בעל ההשפעה הגדולה ביותר על ציון הבריאות שלך.",
        "Several heart-risk signals are raised at once. This is worth discussing with a doctor and reviewing preventive steps.":
            "כמה סימני סיכון לב מוגברים בו-זמנית. כדאי להתייעץ עם רופא ולבחון צעדים מונעים.",
    }
    if s in mapping:
        return mapping[s]

    # Patterns
    m = re.match(r"^Over time, your (.+?) keeps moving in the wrong direction\. Trends like this are easy to miss in single visits\.$", s)
    if m:
        return (f"לאורך זמן, {_label(m.group(1).title())} שלך ממשיך בכיוון לא רצוי. "
                "מגמות כאלה קל לפספס בביקור בודד.")
    # Generic patterns
    m = re.match(r"^(.+?) is slightly outside the ideal range\.$", s)
    if m:
        return f"{_label(m.group(1))} מעט מחוץ לטווח האידיאלי."
    m = re.match(r"^(.+?) is outside the usual range and worth a closer look\.$", s)
    if m:
        return f"{_label(m.group(1))} מחוץ לטווח הרגיל וכדאי לבחון לעומק."

    # Insurance plain
    if "You appear to be paying more than once" in s:
        m2 = re.search(r"for ([a-z /]+)", s)
        what = _coverage((m2.group(1) if m2 else "").strip().capitalize())
        return f"נראה שאתה משלם יותר מפעם אחת על {what}. איחוד יכול לחסוך ללא ויתור על כיסוי."
    if "You don't seem to have" in s:
        m2 = re.search(r"have ([a-z /]+)\.", s)
        what = _coverage((m2.group(1) if m2 else "").strip().capitalize())
        return f"לא נראה שיש לך {what}. נחשב חיוני — כדאי לבחון."
    if "At your age," in s and "may not give you the value it once did" in s:
        return "בגילך, הכיסוי הזה עשוי כבר לא להעניק לך את הערך שפעם נתן. כדאי לבדוק התאמה."
    if "One policy makes up most of your insurance spend" in s:
        return "פוליסה אחת מהווה את רוב הוצאות הביטוח שלך — ודא שהיא מותאמת לסיכון ושווה את ההשקעה."
    if "renews soon — a good moment to review" in s:
        m2 = re.search(r"Your ([a-z /]+) renews", s)
        what = _coverage((m2.group(1) if m2 else "").strip().capitalize())
        return f"{what} מתחדש בקרוב — זמן טוב לבחון התאמה לצרכים שלך."
    # Drug interactions plain
    m = re.match(r"^Taking (.+?) and (.+?) together is worth reviewing with your pharmacist or doctor\.$", s)
    if m:
        return f"השילוב של {_drug(m.group(1))} ו-{_drug(m.group(2))} כדאי לבחון עם רוקח/רופא."
    if s == "You may be taking two medicines that do the same job — worth confirming this is intended.":
        return "ייתכן שאתה נוטל שתי תרופות לאותה מטרה — כדאי לוודא שזה מכוון."
    # Family
    if "Your family history suggests a higher-than-average" in s:
        m2 = re.search(r"higher-than-average ([a-z- /]+)\. ", s)
        risk = (m2.group(1) if m2 else "").strip()
        risk_he = {"cardiovascular risk": "סיכון קרדיווסקולרי",
                   "metabolic risk": "סיכון מטבולי",
                   "breast-cancer risk": "סיכון לסרטן שד",
                   "ovarian/BRCA risk": "סיכון BRCA/שחלות",
                   "colorectal-cancer risk": "סיכון לסרטן מעי",
                   "prostate-cancer risk": "סיכון לסרטן ערמונית",
                   "skin-cancer risk": "סיכון לסרטן עור"}.get(risk, risk)
        return f"ההיסטוריה המשפחתית מצביעה על {risk_he} מעל הממוצע. ייתכן שיהיה כדאי להקדים בדיקות מונעות — כדאי להתייעץ עם רופא."
    # Emergency
    if "One of your readings is in a range" in s:
        return ("אחת התוצאות שלך נמצאת בטווח שאנו ממליצים לבדוק אצל איש מקצוע רפואי בהקדם. "
                "אם אתה מרגיש לא טוב — פנה לטיפול דחוף.")
    # Cross-correlation
    if "Several blood markers point to low iron together" in s:
        return ("כמה מרקרים בדם מצביעים יחד על ברזל נמוך — שילוב שכדאי להעלות בפני רופא, "
                "מכיוון שיש לכך סיבות הניתנות לטיפול.")
    if "A few markers related to blood sugar and fats" in s:
        return ("כמה מרקרים הקשורים לסוכר ושומנים מוגברים יחד. "
                "בשלב זה שינויי אורח חיים יעילים מאוד — כדאי לדבר על זה.")
    if "A few liver-related values are raised together" in s:
        return "כמה ערכים הקשורים לכבד מוגברים יחד — כדאי בדיקת המשך."
    if "Kidney-function markers suggest a follow-up" in s:
        return "מרקרי תפקוד הכליות מצביעים על כך שמומלצת בדיקת המשך אצל רופא."
    # Projection
    m = re.match(r"^At the current pace, your (.+?) may keep moving in the wrong direction\. Acting now is usually easier than later\.$", s)
    if m:
        return (f"בקצב הנוכחי, {_label(m.group(1).title())} עלול להמשיך בכיוון לא רצוי. "
                "פעולה עכשיו לרוב קלה יותר מאשר בהמשך.")
    # Screening 'why'
    why_map = {
        "Colorectal cancer is highly treatable when found early through routine screening.":
            "סרטן מעי גס ניתן לטיפול יעיל כשמתגלה מוקדם דרך סקירה שגרתית.",
        "Regular mammograms help detect breast cancer before symptoms appear.":
            "ממוגרפיה שגרתית עוזרת לזהות סרטן שד לפני הופעת תסמינים.",
        "A family history of breast/ovarian cancer can justify genetic counseling.":
            "היסטוריה משפחתית של סרטן שד/שחלות עשויה להצדיק ייעוץ גנטי.",
        "HPV/Pap testing detects pre-cancerous cervical changes early.":
            "בדיקות פאפ/HPV מזהות שינויים טרום-סרטניים בצוואר הרחם מוקדם.",
        "Discuss PSA testing with a clinician to weigh benefits and risks.":
            "התייעץ עם רופא לגבי בדיקת PSA לשקלול תועלת אל מול סיכון.",
        "Lipid screening identifies cardiovascular risk that is treatable.":
            "סקירת שומנים מזהה סיכון קרדיווסקולרי שניתן לטיפול.",
        "Early detection of high blood sugar prevents long-term complications.":
            "זיהוי מוקדם של סוכר גבוה מונע סיבוכים ארוכי טווח.",
        "High blood pressure is common, silent, and treatable.":
            "לחץ דם גבוה נפוץ, שקט, וניתן לטיפול.",
        "Periodic skin checks help catch suspicious lesions early.":
            "בדיקות עור תקופתיות עוזרות לאתר נגעים חשודים מוקדם.",
        "One-time ultrasound is recommended for men 65-75 who have ever smoked.":
            "אולטרסאונד חד-פעמי מומלץ לגברים בני 65–75 שעישנו אי פעם.",
    }
    if s in why_map:
        return why_map[s]
    if s == "Smoking increases cardiovascular and cancer risk across the board.":
        return "עישון מעלה סיכון קרדיווסקולרי וסרטני באופן רוחבי."
    if s == "Multiple heart-related markers are elevated together":
        return "כמה מרקרים הקשורים ללב מוגברים יחד"
    # Second-opinion canned phrases
    second_op = {
        "Ask whether the cause of low iron has been investigated (diet, blood loss, absorption).":
            "שאל אם הסיבה לברזל נמוך נבדקה (תזונה, איבוד דם, ספיגה).",
        "Ask if a ferritin + reticulocyte panel would clarify the picture.":
            "שאל האם בדיקת פריטין + רטיקולוציטים תבהיר את התמונה.",
        "Ask whether a coronary risk calculator (e.g. ASCVD) applies to you.":
            "שאל אם מחשבון סיכון קורונרי (למשל ASCVD) רלוונטי עבורך.",
        "Ask if a one-time lipoprotein(a) test is worthwhile given family history.":
            "שאל האם בדיקת ליפופרוטאין(a) חד-פעמית מוצדקת בהתחשב בהיסטוריה משפחתית.",
        "Ask whether a repeat fasting glucose or oral glucose tolerance test is indicated.":
            "שאל האם בדיקת גלוקוז בצום חוזרת או בדיקת העמסת סוכר מוצדקת.",
        "Ask about a structured lifestyle program before considering medication.":
            "שאל על תוכנית אורח חיים מובנית לפני שקילת תרופות.",
        "Ask whether a liver ultrasound or a fatty-liver evaluation is appropriate.":
            "שאל האם אולטרסאונד כבד או הערכה לכבד שומני מתאימים.",
        "Ask whether a urine albumin test should accompany the eGFR.":
            "שאל אם בדיקת אלבומין בשתן צריכה ללוות את ה-eGFR.",
        "Ask whether free T4 / antibodies should be checked alongside TSH.":
            "שאל אם יש לבדוק free T4 / נוגדנים יחד עם TSH.",
    }
    if s in second_op:
        return second_op[s]
    return s


def _t_score_component(c: ScoreComponent) -> ScoreComponent:
    domain = DOMAIN_HE.get(c.domain, c.domain)
    note = c.note
    m = re.match(r"^(\d+) marker\(s\) measured$", note)
    if m:
        note = f"{m.group(1)} מרקרים נמדדו"
    elif note == "No data yet":
        note = "אין נתונים עדיין"
    return ScoreComponent(domain=domain, score=c.score, note=note)


def _t_trend(t: MarkerTrend) -> MarkerTrend:
    return MarkerTrend(
        marker=t.marker,
        label=MARKER_LABELS_HE.get(t.label, t.label),
        unit=t.unit,
        points=t.points,
        direction=t.direction,
        status=t.status,
    )


def _t_finding(f: Finding) -> Finding:
    return Finding(
        title=_t_title(f.title),
        detail=_t_detail(f.detail),
        priority=f.priority,
        source=f.source,
        plain_language=_t_plain(f.plain_language) if f.plain_language else "",
    )


# ---- Public API ----------------------------------------------------------

DISCLAIMER_HE = (
    "מערכת זו אינה מספקת אבחנה רפואית ואינה תחליף להתייעצות "
    "עם איש מקצוע רפואי מוסמך."
)


def translate_report(report: HealthReport, lang: str) -> HealthReport:
    if lang != "he":
        return report

    return HealthReport(
        user=report.user,
        health_score=report.health_score,
        score_components=[_t_score_component(c) for c in report.score_components],
        top_priorities=[_t_finding(f) for f in report.top_priorities],
        findings=[_t_finding(f) for f in report.findings],
        trends=[_t_trend(t) for t in report.trends],
        missing_screenings=[_t_finding(f) for f in report.missing_screenings],
        insurance_insights=[_t_finding(f) for f in report.insurance_insights],
        notifications=[_t_finding(f) for f in report.notifications],
        emergency_alerts=[_t_finding(f) for f in report.emergency_alerts],
        drug_interactions=[_t_finding(f) for f in report.drug_interactions],
        family_insights=[_t_finding(f) for f in report.family_insights],
        coverage_matches=[_t_finding(f) for f in report.coverage_matches],
        projections=[_t_finding(f) for f in report.projections],
        percentiles=[
            type(p)(
                marker=p.marker,
                label=MARKER_LABELS_HE.get(p.label, p.label),
                value=p.value,
                percentile=p.percentile,
                higher_is_risk=p.higher_is_risk,
            )
            for p in report.percentiles
        ],
        second_opinions=[_t_finding(f) for f in report.second_opinions],
        insurance_negotiation=[_t_finding(f) for f in report.insurance_negotiation],
        claim_opportunities=[_t_finding(f) for f in report.claim_opportunities],
        disclaimer=DISCLAIMER_HE,
    )
