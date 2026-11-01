#!/usr/bin/env python3
"""check.py: CV, ön yazı ve form metinleri için dürüstlük, yasak ifade ve ATS kontrolü.

Bağımlılık: yok (yalnız Python standart kütüphanesi). build_cv.py bu dosyayı içe aktarır.

Kullanım (<skill> = bu skill'in klasörü; diğer yollar çalıştığın klasöre göre):
  python <skill>/scripts/check.py --profile profile.json
      profilin tamamını tarar (bütün maddeler dahil): kurulumda ve her profil değişikliğinde
  python <skill>/scripts/check.py --profile profile.json --job job.json
      ilana özel seçimi tarar (CV metni + varsa ön yazı); dosya üretmez
  python <skill>/scripts/check.py --profile profile.json --text message.txt [--text form.txt] [--job job.json]
      serbest metin tarar: ön yazı, form cevabı, işe alımcıya mesaj, takip maili
  ... --text answer.txt --answer
      doğrudan sorulmuş bir soruya dürüst cevap ("SAP kullandın mı?"): eksiği söylemek ve kullanılmayan
      programı anmak HATA değil KONTROL olur (B11, F4)

Çıkış kodu: 0 = temiz (yalnız KONTROL uyarısı olabilir) · 1 = en az bir HATA · 2 = dosya, yapı ya da program sorunu.
HATA düzeltilmeden çıktı kişiye verilmez. KONTROL maddeleri gerçekle karşılaştırılır, gerekiyorsa kişiye sorulur.
"""

import argparse
import json
import re
import sys
import unicodedata
from itertools import permutations

# level "error" -> HATA (çıkış kodu 1) · "check" -> KONTROL (yalnız uyarı).
# kapsam: "cv" yalnız CV'de, "metin" yalnız ön yazı/form/mesajda, "hepsi" ikisinde de.
# korpus_muaf: eşleşen ifade kişinin onayladığı profilde de geçiyorsa uyarı verilmez.
# cevap_uyari: --cevap modunda HATA yerine KONTROL.
# Kişi bir kuralı bilerek kapatmak isterse id'sini profile.json "lintAllow" listesine yazar.
# Kalıplar İngilizce + sık CV dillerindeki karşılıkları (tr, de, pl, es, fr, it, nl). Rakam, program ve
# "asla yazma" kontrolleri dilden bağımsızdır.
KURALLAR = [
    {"id": "looking-for", "level": "error", "kapsam": "cv", "kural": "C2",
     "re": r"\blooking for\b|\b(?:pozisyon|iş|rol) arıyorum\b|\bsuche (?:eine|einen|nach)\b|\bbusco (?:un|una)\b|"
           r"\bszukam\b|\bje recherche\b|\bcerco (?:un|una)\b|\bik zoek\b",
     "msg": "'Looking for…' yasak: ne aradığını değil ne getirdiğini yaz"},
    {"id": "looking-for", "level": "check", "kapsam": "metin", "kural": "C2",
     "re": r"\b(I am|I'm) looking for\b", "msg": "'I'm looking for…' ile başlama: rol ve getirdiğin değerle başla"},
    {"id": "ai-yardim", "level": "error", "kapsam": "hepsi", "kural": "C10",
     "re": r"AI[- ]assist|with (the help of )?(AI|ChatGPT|artificial intelligence)\b|using (AI|ChatGPT)\b|"
           r"yapay zek[aâ] (?:yardımıyla|desteğiyle)|\bmit (?:Hilfe von )?KI\b|\bcon (?:ayuda de )?(?:la )?IA\b|"
           r"z pomocą (?:AI|SI)\b|avec l'IA\b|con l'IA\b|met behulp van AI\b",
     "msg": "yapay zekâ kullanımı yetkinlik gibi yazılmaz ('with AI assistance' vb.)"},
    {"id": "ogrenme", "level": "error", "kapsam": "hepsi", "kural": "C3/D2",
     "re": r"\b(want|like|keen|eager|hope|hoping) to (learn|build|develop|grow)\b|\bwhere I can (learn|build|develop|grow)\b|"
           r"\bopportunity to (learn|grow)\b|öğrenmek istiyorum|öğrenebileceğim|möchte (?:\w+ )?(?:lernen|dazulernen)|"
           r"\bquiero aprender\b|chcę się (?:\w+ )?nauczyć|souhaite apprendre|vorrei imparare|wil (?:graag )?leren",
     "msg": "'öğrenmek istiyorum' çerçevesi: ne getirdiğini yaz"},
    {"id": "eksik-itiraf", "level": "error", "kapsam": "hepsi", "kural": "C4", "cevap_uyari": True,
     "re": r"\bhaven'?t (yet )?(used|worked)\b|\bhave not (yet )?(used|worked)\b|\bno experience\b|\bdon'?t have\b|"
           r"\blimited experience\b|\bnot (yet )?familiar\b|\bI lack\b|deneyimim yok|\bkullanmadım\b|"
           r"keine Erfahrung|no tengo experiencia|nie mam doświadczenia|pas d'expérience|nessuna esperienza|geen ervaring",
     "msg": "eksiği kendiliğinden söylemek: soru gelmeden eksik yazılmaz"},
    {"id": "bos-sifat", "level": "error", "kapsam": "hepsi", "kural": "C5",
     "re": r"\b(?:results[- ]driven|dynamic professional|passionate|highly motivated|team player|self[- ]starter|"
           r"go[- ]getter|fast learner|quick learner|hard[- ]?working|detail[- ]oriented|think outside the box|"
           r"can do any job|tutkulu\w*|sonuç odaklı\w*|takım oyuncusu\w*|yüksek motivasyonlu\w*|hızlı öğrenen\w*|detay odaklı\w*|"
           r"leidenschaftlich|hochmotiviert|ergebnisorientiert|Teamplayer|apasionad[oa]|orientad[oa] a resultados|"
           r"altamente motivad[oa]|pasjonat\w*|zorientowan[ya] na wyniki|passionn[ée]e?|orienté résultats|"
           r"appassionat[oa]|orientat[oa] ai risultati|gepassioneerd|resultaatgericht)\b",
     "msg": "boş sıfat ya da kanıtsız iddia: yerine somut iş ya da rakam yaz"},
    {"id": "bos-ovgu", "level": "error", "kapsam": "hepsi", "kural": "D2",
     "re": r"\b(?:prestigious|amazing opportunity|dream (?:job|company|role)|world[- ]class|industry[- ]leading|"
           r"esteemed|prestijli|renommiert\w*|prestigios[oa]|prestiżow\w*|prestigieu(?:x|se))\b",
     "msg": "boş övgü: şirket hakkında yalnız ilanda yazanı kullan"},
    {"id": "excel-seviye", "level": "error", "kapsam": "hepsi", "kural": "A6",
     "re": r"\b(advanced|expert|excellent|strong|good|proficient)\s+(knowledge of\s+|skills in\s+|in\s+)?"
           r"(MS\s+|Microsoft\s+)?Excel\b|\bExcel\s*[,:(-]?\s*(advanced|expert|excellent|good)\b|"
           r"ileri (?:düzey|seviye) Excel|Excel(?:'de)? ileri (?:düzey|seviye)|fortgeschrittene\w* Excel|"
           r"sehr gute\w* Excel|Excel avanzado|zaawansowan\w* Excel|Excel avancé|Excel avanzato|gevorderd\w* Excel",
     "msg": "kanıtsız Excel seviyesi: yapabildiği somut işi yaz (filtre, lookup, pivot…). Kanıt varsa lintAllow'a 'excel-seviye' eklenir"},
    {"id": "tire-ok", "level": "error", "kapsam": "hepsi", "kural": "C9",
     "re": r"—|→|⇒", "msg": "uzun tire ya da ok işareti (yapay zekâ kokusu): virgül ya da nokta kullan"},
    {"id": "yil", "level": "check", "kapsam": "hepsi", "kural": "A5", "korpus_muaf": True,
     "re": r"\b(\d+\+?|one|two|three|four|five|six|seven|eight|nine|ten)\s+(years?|yrs)\b|"
           r"\b\d+\+?\s+(?:yıl|yıllık|Jahre?n?|años|lat|ans|anni|jaar)\b",
     "msg": "yıl iddiası: tarihlerle birebir tutuyor mu, ayrı işler birleştirilmiş mi?"},
    {"id": "yuzde", "level": "check", "kapsam": "hepsi", "kural": "A1", "korpus_muaf": True,
     "re": r"\d+(?:[.,]\d+)?\s?%|%\s?\d+", "msg": "yüzde rakamı: kişi bunu kanıtlayabilir mi?"},
    {"id": "dil-seviye", "level": "check", "kapsam": "hepsi", "kural": "A6/E4", "korpus_muaf": True,
     "re": r"\b(fluent|bilingual|native[- ]level|near[- ]native|expert|proficient|akıcı|fließend|"
           r"verhandlungssicher|fluido|fluente|biegł\w*|courant)\b",
     "msg": "seviye iddiası: profildeki dürüst seviyeyle aynı mı?"},
]

# Profilde geçmiyorsa çıktıda yazılmayacak program ve sistemler (A3). Büyük/küçük harfe duyarlı aranır
# ("every workday" ≠ "Workday"). Kişiye özel yasaklar profile.json "neverWrite" ve "notDone" listelerindedir.
ARACLAR = [
    "SAP", "S/4HANA", "SAP Business One", "Oracle", "NetSuite", "Microsoft Dynamics", "Dynamics 365", "Dynamics NAV",
    "Navision", "Business Central", "Salesforce", "HubSpot", "Pipedrive", "Zoho", "Zendesk", "Freshdesk",
    "Freshworks", "ServiceNow", "Intercom", "Genesys", "Five9", "Avaya", "Jira", "Confluence", "Asana", "Trello",
    "Monday.com", "Workday", "SuccessFactors", "QuickBooks", "Xero", "Sage", "Ariba", "Coupa", "Concur", "IFS",
    "Infor", "JD Edwards", "Epicor", "Odoo", "Comarch", "Optima", "Symfonia", "enova365", "Subiekt", "InsERT",
    "Rewizor", "wFirma", "iFirma", "Fakturownia", "Logo Tiger", "Logo Go", "Netsis", "Mikro", "Nebim", "Paraşüt",
    "Tableau", "Power BI", "Power Query", "Qlik", "Looker", "SQL", "Python", "VBA", "Amadeus", "Sabre", "Galileo",
    "ERP", "CRM", "WMS", "TMS",
]

# Yazıyla yazılmış sayılar da rakam gibi kontrol edilir ("team of eight"). "one" sık geçtiği için yok.
SAYI_KELIME = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
               "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
               "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
               "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
               "hundreds": 100, "thousand": 1000, "thousands": 1000, "dozen": 12, "dozens": 12}
BIRLER = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}
AYLAR = (r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*|"
         r"(?:Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)")
# Rakam kontrolünden önce silinir: telefon, e-posta, link, tam tarih, saat (bunlar deneyim iddiası değil).
SAYI_DISI = [
    re.compile(r"\S+@\S+|https?://\S+|www\.\S+|linkedin\.com/\S*"),
    re.compile(r"\+\d{1,3}[\s\d()-]{6,}\d|\b\d{3}[\s-]\d{3}[\s-]\d{3}\b"),
    re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{AYLAR})\s+\d{{4}}\b|\b(?:{AYLAR})\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}\b",
               re.IGNORECASE),
    re.compile(r"\b\d{1,2}:\d{2}\b"),
]
DOLGU = {"a", "an", "the", "of", "in", "on", "for", "to", "and", "with", "at", "by", "my", "our", "any"}

PROFIL_ZORUNLU = ["name", "contact", "profile", "jobs", "experience", "education", "languages"]
ILAN_ALANLARI = {"company", "role", "family", "link", "city", "country", "cvPages", "jobAd", "headline", "profile", "skills",
                 "experience", "other", "gdpr", "coverLetter", "educationFirst"}
# Bu alanlar "gerçek" değil; korpusa girmez (ör. notDone'da "SAP" yazması SAP'a izin vermez).
KORPUS_DISI = {"neverWrite", "notDone", "lintAllow", "gdpr", "headings", "educationFirst", "futureRecruitment"}

# CV bölüm başlıkları (standart adlar; başvuru sistemleri bunları tanır). CV dili profilde "cvLanguage"
# (ISO kodu: en, de, tr…). Listede olmayan bir dil için profile "headings" yazılır (aynı anahtarlarla).
BASLIK_ANAHTARLARI = ("profile", "skills", "experience", "other", "projects", "education", "languages", "it")
BASLIKLAR = {
    "en": ("Profile", "Core Skills", "Work Experience", "Other Experience", "Projects", "Education", "Languages",
           "IT Skills"),
    "tr": ("Profil", "Temel Yetkinlikler", "İş Deneyimi", "Diğer Deneyimler", "Projeler", "Eğitim", "Diller",
           "Bilgisayar Becerileri"),
    "de": ("Profil", "Kernkompetenzen", "Berufserfahrung", "Weitere Erfahrung", "Projekte", "Ausbildung", "Sprachen",
           "IT-Kenntnisse"),
    "pl": ("Profil", "Kluczowe umiejętności", "Doświadczenie zawodowe", "Inne doświadczenie", "Projekty",
           "Wykształcenie", "Języki", "Umiejętności IT"),
    "fr": ("Profil", "Compétences clés", "Expérience professionnelle", "Autres expériences", "Projets", "Formation",
           "Langues", "Informatique"),
    "es": ("Perfil", "Competencias clave", "Experiencia profesional", "Otra experiencia", "Proyectos", "Formación",
           "Idiomas", "Informática"),
    "it": ("Profilo", "Competenze chiave", "Esperienza professionale", "Altre esperienze", "Progetti",
           "Istruzione e formazione", "Lingue", "Competenze informatiche"),
    "nl": ("Profiel", "Kerncompetenties", "Werkervaring", "Overige ervaring", "Projecten", "Opleiding", "Talen",
           "IT-vaardigheden"),
    "pt": ("Perfil", "Competências principais", "Experiência profissional", "Outras experiências", "Projetos",
           "Formação", "Idiomas", "Informática"),
}
# Veri işleme onay cümlesi yalnız geleneksel olduğu ülkelerde kendiliğinden eklenir (başvurulan ülke: ilanda
# ya da profilde "country"). Başka yerde ilan isterse "gdpr" alanına yazılır; istenmiyorsa "gdpr": "".
ONAY_CUMLELERI = {
    "pl": {"en": "I hereby consent to the processing of my personal data included in this application for the "
                 "purposes of the recruitment process, in accordance with Regulation (EU) 2016/679 (GDPR).",
           "pl": "Wyrażam zgodę na przetwarzanie moich danych osobowych zawartych w niniejszym dokumencie dla "
                 "potrzeb niezbędnych do realizacji procesu rekrutacji, zgodnie z Rozporządzeniem (UE) 2016/679 (RODO)."},
    "it": {"en": "I authorise the processing of my personal data for recruitment purposes pursuant to Regulation "
                 "(EU) 2016/679 (GDPR).",
           "it": "Autorizzo il trattamento dei miei dati personali ai fini della selezione del personale ai sensi "
                 "del Regolamento (UE) 2016/679 (GDPR)."},
}
# Kişi profilde "futureRecruitment": true dediyse (gelecekteki işe alımlar için de izin) bu sürüm kullanılır.
ONAY_GELECEK = {
    "pl": {"en": "I hereby consent to the processing of my personal data included in this application for the "
                 "purposes of current and future recruitment processes, in accordance with Regulation (EU) "
                 "2016/679 (GDPR).",
           "pl": "Wyrażam zgodę na przetwarzanie moich danych osobowych zawartych w niniejszym dokumencie dla "
                 "potrzeb obecnych i przyszłych procesów rekrutacji, zgodnie z Rozporządzeniem (UE) 2016/679 (RODO)."},
}
ULKE_ADLARI = {"poland": "pl", "polska": "pl", "polonya": "pl", "italy": "it", "italia": "it", "italya": "it"}


def ulke_kodu(deger):
    s = unicodedata.normalize("NFKD", str(deger or "")).encode("ascii", "ignore").decode().strip().lower()
    return ULKE_ADLARI.get(s, s)


class GirdiHatasi(Exception):
    """Dosya okunamadı ya da yapı bozuk: çıkış kodu 2."""


def oku_json(yol):
    try:
        with open(yol, encoding="utf-8-sig") as f:
            metin = f.read()
    except OSError as e:
        raise GirdiHatasi(f"{yol} okunamadı: {e}")
    try:
        return json.loads(metin)
    except json.JSONDecodeError as e:
        ipucu = " Akıllı tırnak (“ ”) var: düz tırnakla (\") yeniden yaz." if re.search("[“”„]", metin) else ""
        raise GirdiHatasi(f"{yol} geçerli JSON değil: {e}.{ipucu}")


def oku_metin(yol):
    try:
        with open(yol, encoding="utf-8-sig") as f:
            return f.read()
    except OSError as e:
        raise GirdiHatasi(f"{yol} okunamadı: {e}")


def _degerler(x, anahtar=None, haric=frozenset()):
    """JSON içindeki bütün metin değerlerini düz bir listeye toplar ("_" ile başlayan notlar hariç)."""
    if anahtar is not None and (str(anahtar).startswith("_") or anahtar in KORPUS_DISI or anahtar in haric):
        return []
    if isinstance(x, dict):
        return [s for k, v in x.items() for s in _degerler(v, k, haric)]
    if isinstance(x, list):
        return [s for v in x for s in _degerler(v, None, haric)]
    if isinstance(x, (str, int, float)) and not isinstance(x, bool):
        return [str(x)]
    return []


def profil_korpusu(P, haric=frozenset()):
    return "\n".join(_degerler(P, None, haric))


def _sayilar(metin):
    """Metindeki rakamlar ve yazıyla yazılmış sayılar (telefon, e-posta, tam tarih ve saat hariç)."""
    for kalip in SAYI_DISI:
        metin = kalip.sub(" ", metin)
    sonuc = {re.sub(r"[.,]", "", m) for m in re.findall(r"(?<![\w])\d+(?:[.,]\d{3})*(?:[.,]\d+)?", metin)}
    kucuk = metin.lower()
    for onlar, birler in re.findall(r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-(one|two|three|four|"
                                    r"five|six|seven|eight|nine)\b", kucuk):
        sonuc.add(str(SAYI_KELIME[onlar] + BIRLER[birler]))
    kucuk = re.sub(r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-\w+", " ", kucuk)
    for kelime in re.findall(r"[a-z]+", kucuk):
        if kelime in SAYI_KELIME:
            sonuc.add(str(SAYI_KELIME[kelime]))
    return sonuc


def _kelime_re(ifade, harf_duyarli=False):
    return re.compile(r"(?<![\w])" + re.escape(str(ifade)) + r"(?![\w])", 0 if harf_duyarli else re.IGNORECASE)


def _benzer_re(ifade):
    """Çok kelimeli 'yapmadım' ifadesinin yakın biçimleri: "managing a team" → "managed a team of",
    "team management". Kelime kökleri (ilk 4 harf) herhangi sırada, aralarında en fazla 3 kelime."""
    kokler = [w[:4] for w in re.findall(r"[a-z]+", str(ifade).lower()) if w not in DOLGU and len(w) >= 3]
    if not 2 <= len(kokler) <= 3:
        return None
    aralik = r"\w*(?:\W+\w+){0,3}?\W+"
    return re.compile("|".join(r"\b" + aralik.join(map(re.escape, sira)) + r"\w*" for sira in permutations(kokler)),
                      re.IGNORECASE)


def metni_tara(metin, P, kapsam="cv", serbest=False, haric=(), ilan_metni="", cevap=False):
    """Bir metni kurallara göre tarar.
    serbest=True: metin profilden birebir gelmiyor (başlık, profil paragrafı, ön yazı…); profilde olmayan
      rakam da aranır.
    haric: başvurulan şirketin ve rolün adı (şirketin adı "Oracle" ise program sayılmaz).
    ilan_metni: yalnız ön yazı/mesajda; ilandaki rakamlar (maaş, vardiya) anılabilir. CV'de kullanılmaz.
    cevap=True: doğrudan sorulmuş soruya dürüst cevap; eksik ve kullanılmayan program KONTROL olur."""
    izin = set(P.get("lintAllow", []))
    korpus = profil_korpusu(P)
    sonuc = []
    for r in KURALLAR:
        if r["id"] in izin or r["kapsam"] not in ("hepsi", kapsam):
            continue
        eslesmeler = [m.group(0) for m in re.finditer(r["re"], metin, re.IGNORECASE)]
        if r.get("korpus_muaf"):
            eslesmeler = [e for e in eslesmeler if e.lower() not in korpus.lower()]
        if eslesmeler:
            seviye = "check" if cevap and r.get("cevap_uyari") else r["level"]
            ornek = ", ".join(sorted(set(eslesmeler))[:3])
            sonuc.append((seviye, f"{r['msg']} [{r['kural']}]: bulunan \"{ornek}\""))

    yasak_seviye = "check" if cevap else "error"
    for liste, ad in ((P.get("neverWrite", []), "asla yazma"), (P.get("notDone", []), "yapmadım")):
        for ifade in liste:
            if not ifade:
                continue
            if _kelime_re(ifade).search(metin):
                sonuc.append((yasak_seviye if ad == "yapmadım" else "error",
                              f"kişinin '{ad}' listesi: \"{ifade}\" [A10]"))
                continue
            benzer = _benzer_re(ifade)
            m = benzer.search(metin) if benzer else None
            if m:
                sonuc.append((yasak_seviye if ad == "yapmadım" else "error",
                              f"kişinin '{ad}' listesine çok benziyor: \"{ifade}\" ~ \"{m.group(0)}\" [A10]"))

    haric_metin = " ".join(str(h) for h in haric if h)
    for arac in ARACLAR:
        if f"arac:{arac}" in izin or _kelime_re(arac).search(korpus) or _kelime_re(arac).search(haric_metin):
            continue
        if _kelime_re(arac, harf_duyarli=True).search(metin):
            sonuc.append((yasak_seviye, f"profilde olmayan program/sistem: \"{arac}\" [A3]. Kişi gerçekten "
                                        f"kullandıysa önce profile eklenir" +
                          (" (cevapta yalnız 'kullanmadım' anlamında geçmeli)" if cevap else "")))

    if serbest:
        bilinen = (_sayilar(profil_korpusu(P, frozenset({"contact"}))) | _sayilar(haric_metin)
                   | _sayilar(ilan_metni or ""))
        yabanci = sorted((n for n in _sayilar(metin) - bilinen if f"rakam:{n}" not in izin), key=lambda s: int(s))
        if yabanci:
            sonuc.append(("error", f"profilde olmayan rakam/sayı: {', '.join(yabanci)} [A1]. Rakam yalnız onaylı "
                                   f"profilden gelir (yazıyla yazılan sayılar da)"))
    return sonuc


# ─── yapı (şema) kontrolü ──────────────────────────────────────────────────────

def _metin_listesi(deger, ad, sonuc):
    if deger is None:
        return
    if not isinstance(deger, list) or not all(isinstance(x, str) for x in deger):
        sonuc.append(("error", f"'{ad}' metin listesi olmalı: [\"…\", \"…\"]"))


def _metin(deger, ad, sonuc):
    if deger is not None and not isinstance(deger, str):
        sonuc.append(("error", f"'{ad}' tek bir metin olmalı (liste değil); öğeleri ' · ' ile ayır"))


def _secim_listesi(deger, ad, sonuc):
    if deger is None:
        return
    if not isinstance(deger, list):
        sonuc.append(("error", f"'{ad}' liste olmalı: [[\"is\", [\"madde\", …]], …]"))
        return
    for e in deger:
        ok = (isinstance(e, list) and len(e) >= 1 and isinstance(e[0], str)
              and (len(e) == 1 or (isinstance(e[1], list) and all(isinstance(m, str) for m in e[1]))))
        ok = ok or (isinstance(e, dict) and isinstance(e.get("job"), str))
        if not ok:
            sonuc.append(("error", f"'{ad}' öğesi [\"is_anahtari\", [\"madde\", …]] biçiminde olmalı: {json.dumps(e, ensure_ascii=False)[:60]}"))


def profil_yapisi(P):
    if not isinstance(P, dict):
        return [("error", "profil bir JSON nesnesi olmalı")]
    # jobs ve experience boş olabilir (ilk işini arayan biri); alan yine de bulunmalı.
    sonuc = [("error", f"profilde zorunlu alan eksik: {a}") for a in PROFIL_ZORUNLU
             if (a not in P if a in ("jobs", "experience") else not P.get(a))]
    for a in ("name", "contact", "headline", "profile", "languages", "itSkills", "country", "cvLanguage"):
        _metin(P.get(a), a, sonuc)
    if P.get("cvPages") is not None and P["cvPages"] not in (1, 2, 3):
        sonuc.append(("error", "'cvPages' 1, 2 ya da 3 olmalı"))
    basliklar = P.get("headings")
    if basliklar is not None and not (isinstance(basliklar, dict) and all(
            k in BASLIK_ANAHTARLARI and isinstance(v, str) for k, v in basliklar.items() if not k.startswith("_"))):
        sonuc.append(("error", f"'headings' {{\"anahtar\": \"başlık\"}} biçiminde olmalı; anahtarlar: "
                               f"{', '.join(BASLIK_ANAHTARLARI)}"))
    for a in ("skills", "neverWrite", "notDone", "lintAllow"):
        _metin_listesi(P.get(a), a, sonuc)
    egitim = P.get("education")
    if egitim is not None and not isinstance(egitim, str):
        _metin_listesi(egitim, "education", sonuc)
    projeler = P.get("projects")
    if projeler is not None and not (isinstance(projeler, list) and all(
            isinstance(p, list) and len(p) == 2 and all(isinstance(x, str) for x in p) for p in projeler)):
        sonuc.append(("error", "'projects' [[\"ad\", \"açıklama\"], …] biçiminde olmalı"))
    if P.get("standardAnswers") is not None and not isinstance(P["standardAnswers"], dict):
        sonuc.append(("error", "'standardAnswers' {\"soru\": \"cevap\"} biçiminde olmalı"))
    isler = P.get("jobs")
    if isler is not None and not isinstance(isler, dict):
        sonuc.append(("error", "'jobs' {\"is_anahtari\": {…}} biçiminde olmalı"))
        isler = {}
    for key, j in (isler or {}).items():
        if not isinstance(j, dict):
            sonuc.append(("error", f"jobs.{key} bir nesne olmalı"))
            continue
        for alan in ("title", "dates"):
            if not j.get(alan):
                sonuc.append(("error", f"jobs.{key}: '{alan}' eksik"))
        for alan in ("title", "org", "place", "dates", "ctx"):
            _metin(j.get(alan), f"jobs.{key}.{alan}", sonuc)
        maddeler = j.get("bullets", {})
        if not isinstance(maddeler, dict) or not all(isinstance(v, str) for v in maddeler.values()):
            sonuc.append(("error", f"jobs.{key}.bullets anahtarlı olmalı: {{\"anahtar\": \"cümle\"}}"))
        if isinstance(j.get("dates"), str) and not re.search(r"\b(19|20)\d{2}\b", j["dates"]):
            sonuc.append(("check", f"jobs.{key}: tarihte yıl yok ('{j['dates']}')"))
    _secim_listesi(P.get("experience"), "experience", sonuc)
    _secim_listesi(P.get("other"), "other", sonuc)
    return sonuc


def ilan_yapisi(J):
    if not isinstance(J, dict):
        return [("error", "ilan seçimi bir JSON nesnesi olmalı")]
    sonuc = []
    for a in ("company", "role", "family", "link", "city", "country", "jobAd", "headline", "profile", "coverLetter"):
        _metin(J.get(a), a, sonuc)
    if J.get("cvPages") is not None and J["cvPages"] not in (1, 2, 3):
        sonuc.append(("error", "'cvPages' 1, 2 ya da 3 olmalı"))
    _metin_listesi(J.get("skills"), "skills", sonuc)
    _secim_listesi(J.get("experience"), "experience", sonuc)
    _secim_listesi(J.get("other"), "other", sonuc)
    return sonuc


# ─── CV içeriği ────────────────────────────────────────────────────────────────

def _is_ogesi(e):
    if isinstance(e, dict):
        return e.get("job"), list(e.get("bullets", [])), "title" in e
    if isinstance(e, (list, tuple)) and e:
        return e[0], list(e[1]) if len(e) > 1 else [], len(e) > 2
    return None, [], False


def cv_icerigi(P, J=None):
    """Profil + ilan seçimini CV içeriğine çevirir. Seçim yalnız profildeki işleri ve maddeleri anahtarla
    seçer; unvan, şirket, tarih ve madde metni değişmez (A2). Döner: (icerik, bulgular)."""
    J = J or {}
    bulgular = []
    for alan in J:
        if alan.startswith("_"):
            continue
        if alan in ("jobs", "name", "education", "languages", "contact", "itSkills", "projects"):
            bulgular.append(("error", f"ilan seçimi gerçekleri değiştiremez: '{alan}' alanı yalnız profilde "
                                      f"durur [A2]"))
        elif alan not in ILAN_ALANLARI:
            bulgular.append(("check", f"ilan seçiminde bilinmeyen alan yok sayıldı: '{alan}'"))

    def isler(liste, diger):
        cikti, gorulen = [], set()
        for e in liste or []:
            key, mkeys, unvan_degisti = _is_ogesi(e)
            j = (P.get("jobs") or {}).get(key)
            if j is None:
                bulgular.append(("error", f"bilinmeyen iş anahtarı: '{key}'"))
                continue
            if unvan_degisti:
                bulgular.append(("error", f"'{key}': unvan ilana göre değiştirilemez [A2]"))
            if key in gorulen:
                bulgular.append(("check", f"'{key}' iki kez seçilmiş"))
            gorulen.add(key)
            if diger and len(mkeys) > 1:
                bulgular.append(("error", f"Other Experience en fazla 1 madde: '{key}' [C8]"))
            maddeler = []
            for m in mkeys:
                metin = (j.get("bullets") or {}).get(m)
                if metin is None:
                    bulgular.append(("error", f"bilinmeyen madde: '{key}.{m}'"))
                else:
                    maddeler.append(metin)
            cikti.append({"key": key, "title": j.get("title", ""), "org": j.get("org", ""),
                          "place": j.get("place", ""), "dates": j.get("dates", ""), "ctx": j.get("ctx", ""),
                          "bullets": maddeler})
        return cikti

    egitim = P.get("education") or []
    icerik = {
        "name": P.get("name", ""),
        "headline": J.get("headline", P.get("headline", "")),
        "contact": P.get("contact", ""),
        "profile": J.get("profile", P.get("profile", "")),
        "skills": J.get("skills", P.get("skills", [])),
        "experience": isler(J.get("experience", P.get("experience")), False),
        "other": isler(J.get("other", P.get("other")), True),
        "education": egitim if isinstance(egitim, list) else [egitim],
        "languages": P.get("languages", ""),
        "itSkills": P.get("itSkills", ""),
        "projects": P.get("projects", []),
        "gdpr": J.get("gdpr", P.get("gdpr")),
        "dil": str(P.get("cvLanguage") or "en").strip().lower()[:2],
        "sayfa": J.get("cvPages") or P.get("cvPages") or 1,
        # Yeni mezun: Eğitim bölümü deneyimden önce gelir.
        "educationFirst": bool(J.get("educationFirst", P.get("educationFirst", False))),
    }
    if icerik["gdpr"] is None:
        ulke = ulke_kodu(J.get("country") or P.get("country"))
        kaynak = ONAY_GELECEK if P.get("futureRecruitment") is True and ulke in ONAY_GELECEK else ONAY_CUMLELERI
        metinler = kaynak.get(ulke, {})
        icerik["gdpr"] = metinler.get(icerik["dil"], metinler.get("en", ""))
    basliklar = dict(zip(BASLIK_ANAHTARLARI, BASLIKLAR.get(icerik["dil"], BASLIKLAR["en"])))
    ozel = P.get("headings") if isinstance(P.get("headings"), dict) else {}
    basliklar.update({k: v for k, v in ozel.items() if k in BASLIK_ANAHTARLARI and isinstance(v, str) and v})
    if icerik["dil"] not in BASLIKLAR and not ozel:
        bulgular.append(("check", f"'{icerik['dil']}' dili için hazır bölüm başlığı yok: profile 'headings' ekle "
                                  f"(şimdilik İngilizce başlıklar)"))
    icerik["basliklar"] = basliklar
    if not icerik["experience"]:
        if icerik["education"] and any(icerik["education"]):
            # İlk işini arayan biri: iş satırı yoksa CV eğitim ve projelerle kurulur.
            icerik["educationFirst"] = True
            bulgular.append(("check", "Work Experience boş: CV eğitim, proje ve becerilerle kuruldu (Eğitim öne "
                                      "alındı). Staj ya da öğrenci işi varsa iş olarak eklenmeli"))
        else:
            bulgular.append(("error", "Work Experience ve Education boş: en az biri gerekli"))
    return icerik, bulgular


def cv_duz_metni(icerik):
    """CV'nin okunacak metni (GDPR cümlesi hariç): tarama ve ATS kontrolü için."""
    satirlar = [icerik["name"], icerik["headline"], icerik["contact"], icerik["profile"],
                " · ".join(icerik["skills"])]
    for j in icerik["experience"] + icerik["other"]:
        satirlar += [j["title"], j["org"], j["place"], j["dates"], j["ctx"], *j["bullets"]]
    satirlar += [*icerik["education"], icerik["languages"], icerik["itSkills"]]
    satirlar += [f"{p[0]} {p[1]}" for p in icerik["projects"]]
    return "\n".join(s for s in satirlar if s)


def ats_kontrol(icerik, P, J=None):
    """C11 ATS kuralları ve unvan dürüstlüğü. Tek sayfa kontrolü PDF üretilince build_cv.py'de yapılır."""
    sonuc = []
    ad = icerik["name"]
    if icerik["dil"] == "en" and not re.fullmatch(r"[A-Za-z .'-]+", ad or ""):
        sonuc.append(("check", "İngilizce CV'de isimde özel harf var: uluslararası başvuru sistemleri bozuk "
                               "okuyabilir, Latin harfli yazım önerilir (Ş yerine S, ł yerine l) [C11]"))
    if ad and ad.isupper():
        sonuc.append(("error", "isim tamamen büyük harf: ATS için normal yazım (Ece Yildirim) [C11]"))
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", icerik["contact"]):
        sonuc.append(("error", "iletişim satırında e-posta yok [C11]"))
    if not re.search(r"\+?\d[\d\s()-]{7,}", icerik["contact"]):
        sonuc.append(("check", "iletişim satırında telefon yok"))
    if len(icerik["headline"]) > 90:
        sonuc.append(("check", f"başlık uzun ({len(icerik['headline'])} karakter): ilk 6 saniyede okunmalı [C1]"))
    if len(icerik["profile"]) > 650:
        sonuc.append(("check", f"profil paragrafı uzun ({len(icerik['profile'])} karakter): 2-4 cümle yeter"))
    if icerik["profile"].lower().startswith(("i am ", "i'm ")):
        sonuc.append(("check", "profil 'I am…' ile başlıyor: ne yaptığınla başla [C2]"))
    for j in icerik["experience"]:
        if not j["bullets"]:
            sonuc.append(("check", f"'{j['key']}' işinde madde yok"))
    toplam = sum(len(j["bullets"]) for j in icerik["experience"])
    if toplam > 14:
        sonuc.append(("check", f"{toplam} madde var: tek sayfa için 8-12 madde genelde yeter"))
    # Başlık ilandaki unvanın aynısıysa ve kişi bu unvanla hiç çalışmadıysa: unvan gibi okunabilir (C13, A4).
    rol = (J or {}).get("role", "")
    unvanlar = [str(j.get("title", "")).lower() for j in (P.get("jobs") or {}).values() if isinstance(j, dict)]
    baslik_ilk = icerik["headline"].split("|")[0].strip().lower()
    if ("baslik-unvan" not in set(P.get("lintAllow", [])) and rol and baslik_ilk and baslik_ilk in rol.lower()
            and not any(baslik_ilk in u or u in baslik_ilk for u in unvanlar if u)):
        sonuc.append(("error", f"başlık ilandaki unvanın aynısı (\"{icerik['headline'].split('|')[0].strip()}\") ama "
                               f"kişi bu unvanla çalışmadı: yaptığı işi anlatan bir başlık seç [C13, A4]"))
    return sonuc


def cv_kontrol(P, J=None):
    """Profil + ilan seçimi için bütün kontroller (PDF'siz). Döner: (icerik, bulgular)."""
    J = J or {}
    icerik, bulgular = cv_icerigi(P, J)
    bulgular += profil_yapisi(P) + ilan_yapisi(J)
    haric = [J.get("company"), J.get("role")]
    bulgular += metni_tara(cv_duz_metni(icerik), P, "cv", haric=haric)
    serbest = "\n".join([J.get("headline", ""), J.get("profile", ""), "\n".join(J.get("skills", []))])
    if serbest.strip():
        # İlandaki rakamlar CV'ye giremez: ilan_metni burada verilmez.
        bulgular += [b for b in metni_tara(serbest, P, "cv", serbest=True, haric=haric)
                     if "profilde olmayan rakam" in b[1]]
    bulgular += ats_kontrol(icerik, P, J)
    return icerik, _tekil(bulgular)


def profil_kontrol(P):
    """Kurulumda: bütün maddeler (varsayılan seçimde olmayanlar da) ve varsayılan CV taranır."""
    _, bulgular = cv_kontrol(P)
    tum_maddeler = [m for j in (P.get("jobs") or {}).values() if isinstance(j, dict)
                    for m in (j.get("bullets") or {}).values() if isinstance(m, str)]
    bulgular += metni_tara("\n".join(tum_maddeler), P, "cv")
    return _tekil(bulgular)


def metin_kontrol(metin, P, J=None, cevap=False):
    """Ön yazı, form cevabı ya da mesaj için kontrol (D1-D3, E)."""
    J = J or {}
    bulgular = metni_tara(metin, P, "metin", serbest=True, haric=[J.get("company"), J.get("role")],
                          ilan_metni=J.get("jobAd"), cevap=cevap)
    kelime = len(re.findall(r"\w+", metin))
    if kelime > 230 and not cevap:
        bulgular.append(("check", f"metin {kelime} kelime: ön yazı kısa olmalı (100-200 kelime) [D1]"))
    if re.search(r"\blearn\w*\W*$", metin.strip(), re.IGNORECASE):
        bulgular.append(("error", "metin 'learn…' ile bitiyor [D2]"))
    return _tekil(bulgular)


def _tekil(bulgular):
    gorulen, cikti = set(), []
    for b in bulgular:
        if b not in gorulen:
            gorulen.add(b)
            cikti.append(b)
    return cikti


def rapor(etiket, bulgular):
    """Bulguları yazdırır. Döner: HATA var mı."""
    for seviye, mesaj in bulgular:
        print(f"  {'HATA   ' if seviye == 'error' else 'KONTROL'} {etiket}: {mesaj}")
    return any(s == "error" for s, _ in bulgular)


def sonuc_satiri(hatali, bulgu_sayisi):
    if hatali:
        return "SONUÇ: HATALI. Düzeltmeden kişiye verme."
    return (f"SONUÇ: TEMİZ: otomatik kontrolden geçti ({bulgu_sayisi} uyarı; KONTROL maddelerini gerçekle "
            "karşılaştır). Kişiye \"doğrulandı\" deme.")


def utf8_cikis():
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _calistir(a):
    try:
        P = oku_json(a.profil)
        J = oku_json(a.ilan) if a.ilan else {}
        metinler = [(yol, oku_metin(yol)) for yol in a.metin]
    except GirdiHatasi as e:
        print(f"  HATA    dosya: {e}")
        return 2
    yapisal = [b for b in profil_yapisi(P) + ilan_yapisi(J) if b[0] == "error"]
    if yapisal:
        rapor("Yapı", yapisal)
        print(sonuc_satiri(True, len(yapisal)))
        return 2

    hatali, sayi = False, 0
    if not a.ilan and not metinler:
        b = profil_kontrol(P)
        hatali |= rapor("Profil", b)
        sayi += len(b)
    if a.ilan and not metinler:
        _, b = cv_kontrol(P, J)
        hatali |= rapor("CV", b)
        sayi += len(b)
        if J.get("coverLetter"):
            b = metin_kontrol(J["coverLetter"], P, J)
            hatali |= rapor("Ön yazı", b)
            sayi += len(b)
    for yol, metin in metinler:
        b = metin_kontrol(metin, P, J, cevap=a.cevap)
        hatali |= rapor(yol, b)
        sayi += len(b)
    print(sonuc_satiri(hatali, sayi))
    return 1 if hatali else 0


def main(argv=None):
    utf8_cikis()
    ap = argparse.ArgumentParser(description="CV, ön yazı ve form metni kontrolü")
    ap.add_argument("--profile", "--profil", dest="profil", required=True, help="kişinin profile.json dosyası")
    ap.add_argument("--job", "--ilan", dest="ilan", help="ilana özel seçim (job.json)")
    ap.add_argument("--text", "--metin", dest="metin", action="append", default=[], help="taranacak düz metin dosyası (tekrarlanabilir)")
    ap.add_argument("--answer", "--cevap", dest="cevap", action="store_true", help="metin, doğrudan sorulmuş bir soruya dürüst cevap")
    a = ap.parse_args(argv)
    try:
        return _calistir(a)
    except Exception as e:  # program hatası: HATA (1) ile karışmasın
        print(f"  HATA    program: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
