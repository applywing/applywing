#!/usr/bin/env python3
"""build_cv.py: profil + ilan seçimi -> ATS dostu CV (DOCX + PDF), Latin, Kiril ve Yunan harfli dillerde, ülkenin sayfa ve fotoğraf
geleneğine göre; varsa ön yazı.

Bağımlılıklar (yoksa otomatik `pip install` denenir):
  python-docx   (import adı: docx)      Word dosyası
  reportlab                             PDF dosyası
  pypdf         (isteğe bağlı)          PDF metninin başvuru sistemlerince okunabildiğini doğrulamak
  pillow        (yalnız --foto ile)     fotoğraf
Aynı klasördeki check.py içe aktarılır (yasak ifade, dürüstlük ve ATS kontrolleri).

Kullanım (<skill> = bu skill'in klasörü; diğer yollar çalıştığın klasöre göre):
  python <skill>/scripts/build_cv.py --profile profile.json --out <klasör>
      varsayılan CV
  python <skill>/scripts/build_cv.py --profile profile.json --job job.json --out <klasör> [--photo foto.jpg]
      ilana uyarlanmış CV (+ job.json'da coverLetter varsa ön yazı)

profile.json: name, contact, headline, profile, skills[], jobs{anahtar: {title, org, place, dates, ctx?,
  bullets{anahtar: metin}}}, experience[[iş, [madde, ...]]], other?[[iş, [0-1 madde]]], education[],
  languages, itSkills?, projects?[[ad, açıklama]], cvLanguage? (en, de, tr, pl, fr, es, it, nl, pt; başka dil
  için headings{}), cvPages? (1-3, varsayılan 1), country?, gdpr?, standardAnswers{}, neverWrite[], notDone[],
  lintAllow[], educationFirst? (yeni mezun: Eğitim deneyimden önce; iş yoksa kendiliğinden).
  Örnek: assets/profile-template.json, examples/profile-en.json
job.json (hepsi isteğe bağlı): company, role, link, city, country, cvPages, jobAd, headline, profile,
  skills[], experience[], other[], gdpr, coverLetter, educationFirst. Seçim yalnız profildeki iş ve madde
  anahtarlarını kullanır; unvan, şirket, tarih ve madde metni değişmez.

Çıkış kodu: 0 = temiz · 1 = en az bir HATA (dosya yazılmaz) · 2 = dosya, yapı ya da program sorunu.
"""

import argparse
import glob
import importlib
import io
import os
import re
import subprocess
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check as kontrol  # noqa: E402

# Görünüm: arkadas/cv-motor şablonundaki ölçüler (pt, mm, renk).
OLCU = {"govde": 9.6, "satir": 1.28, "isim": 19, "baslik": 10.2, "iletisim": 8.8, "bolum": 10, "unvan": 9.9,
        "tarih": 8.8, "meta": 8.8, "baglam": 8.6, "gdpr": 6.8}
KENAR_MM = {"ust": 10, "sag": 13, "alt": 8, "sol": 13}
RENK = {"metin": "1A1A1A", "lacivert": "1F3A5F", "gri": "4A4A4A", "acik_gri": "5A5A5A", "gdpr": "7A7A7A",
        "cizgi": "C3CEDB", "iletisim": "3D3D3D"}
# Sayfaya sığmazsa yazı boyutu bu oranlarla küçültülür; yine sığmazsa HATA.
OLCEKLER = (1.0, 0.96, 0.92)
DOCX_YAZI_TIPI = "Calibri"
FOTO_MM = (28, 34)  # en fazla genişlik, yükseklik

# Unicode yazı tipi adayları (normal, kalın, italik, kalın italik). Liberation Sans = Arial ölçüleri.
YAZI_TIPLERI = {
    "liberation": [("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"),
                   "**/LiberationSans-Regular.ttf"],
    "arial": [("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/ariali.ttf",
               "C:/Windows/Fonts/arialbi.ttf"),
              ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
               "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
               "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf")],
    "dejavu": [("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
               "**/DejaVuSans.ttf", "matplotlib"],
}
SADELESTIR = str.maketrans({"ł": "l", "Ł": "L", "ı": "i", "İ": "I", "ğ": "g", "Ğ": "G", "ş": "s", "Ş": "S",
                            "đ": "d", "Đ": "D", "ø": "o", "Ø": "O", "ß": "ss"})


def paket(import_adi, pip_adi):
    """Paketi içe aktarır; yoksa pip ile kurmayı dener (claude.ai ortamında bazen
    --break-system-packages gerekir). Kurulamazsa None döner."""
    try:
        return importlib.import_module(import_adi)
    except ImportError:
        pass
    for ek in ([], ["--break-system-packages"], ["--user"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", pip_adi, *ek],
                           capture_output=True, text=True)
        if r.returncode == 0:
            importlib.invalidate_caches()
            try:
                return importlib.import_module(import_adi)
            except ImportError:
                continue
    return None


def dosya_adi(metin):
    s = unicodedata.normalize("NFKD", str(metin).translate(SADELESTIR))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_") or "CV"


# ─── PDF (reportlab) ────────────────────────────────────────────────────────────

def _yazi_tipi_dosyalari(secim):
    sirala = ["liberation", "arial", "dejavu"] if secim == "auto" else [secim]
    for aile in sirala:
        for aday in YAZI_TIPLERI.get(aile, []):
            if aday == "matplotlib":
                try:
                    import matplotlib
                    d = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
                    aday = tuple(os.path.join(d, f) for f in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
                                                              "DejaVuSans-Oblique.ttf", "DejaVuSans-BoldOblique.ttf"))
                except ImportError:
                    continue
            elif isinstance(aday, str):
                bulunan = glob.glob(os.path.join("/usr/share/fonts", aday), recursive=True)
                if not bulunan:
                    continue
                d, ad = os.path.split(bulunan[0])
                kok = ad.replace("-Regular.ttf", "").replace(".ttf", "")
                ekler = ("-Bold", "-Italic", "-BoldItalic") if "Liberation" in kok else ("-Bold", "-Oblique", "-BoldOblique")
                aday = (bulunan[0], *(os.path.join(d, kok + e + ".ttf") for e in ekler))
            if all(os.path.exists(f) for f in aday):
                return aile, aday
    return None, None


def pdf_yazi_tipi(secim):
    """Unicode TTF kaydeder. Döner: (normal, kalın, italik, sadeleştirme gerekli mi)."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    if secim != "helvetica":
        aile, dosyalar = _yazi_tipi_dosyalari(secim)
        if dosyalar:
            adlar = [f"CV-{aile}-{i}" for i in range(4)]
            for ad, f in zip(adlar, dosyalar):
                pdfmetrics.registerFont(TTFont(ad, f))
            addMapping(adlar[0], 0, 0, adlar[0])
            addMapping(adlar[0], 1, 0, adlar[1])
            addMapping(adlar[0], 0, 1, adlar[2])
            addMapping(adlar[0], 1, 1, adlar[3])
            return adlar[0], adlar[1], adlar[2], False
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", True


def pdf_olustur(icerik, olcek, yazi_tipi, foto=None):
    """CV PDF'ini bellekte üretir. Döner: (bytes, sayfa sayısı)."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab import rl_config
    from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    rl_config.useA85 = 0  # akışlar ikili sıkıştırılır: dosya daha küçük olur
    normal, kalin, italik, sadelestir = yazi_tipi
    B = icerik["basliklar"]

    def t(s):
        s = _sade(s or "") if sadelestir else str(s or "")
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def boyut(anahtar):
        return OLCU[anahtar] * olcek

    def renk(anahtar):
        return colors.HexColor("#" + RENK[anahtar])

    def stil(ad, anahtar, font=normal, renk_adi="metin", **ek):
        ozellik = {"fontName": font, "fontSize": boyut(anahtar), "leading": boyut(anahtar) * OLCU["satir"],
                   "textColor": renk(renk_adi), "bulletFontName": normal, "bulletFontSize": boyut(anahtar)}
        ozellik.update(ek)
        return ParagraphStyle(ad, **ozellik)

    S = {
        "isim": stil("isim", "isim", kalin, leading=boyut("isim") * 1.15),
        "baslik": stil("baslik", "baslik", kalin, "lacivert", spaceBefore=1, spaceAfter=2),
        "iletisim": stil("iletisim", "iletisim", renk_adi="iletisim"),
        "bolum": stil("bolum", "bolum", kalin, "lacivert", spaceBefore=7 * olcek, spaceAfter=0),
        "govde": stil("govde", "govde", spaceAfter=3 * olcek),
        "satir": stil("satir", "govde", spaceAfter=2 * olcek),
        "unvan": stil("unvan", "unvan", kalin),
        "tarih": stil("tarih", "tarih", renk_adi="gri", alignment=TA_RIGHT),
        "meta": stil("meta", "meta", renk_adi="gri"),
        "baglam": stil("baglam", "baglam", italik, "acik_gri"),
        "madde": stil("madde", "govde", leftIndent=10, bulletIndent=2, spaceAfter=1.4 * olcek),
        "gdpr": stil("gdpr", "gdpr", italik, "gdpr", leading=boyut("gdpr") * 1.22, spaceBefore=6 * olcek),
    }
    # reportlab çerçevesinin iki yanında 6 pt iç boşluk var; tablo bu genişliği aşarsa taşar.
    genislik = A4[0] - (KENAR_MM["sol"] + KENAR_MM["sag"]) * mm - 12

    def bolum(ad):
        return [Paragraph(t(ad), S["bolum"]),
                HRFlowable(width="100%", thickness=0.75, color=renk("cizgi"), spaceBefore=1, spaceAfter=3 * olcek)]

    def satir_tarihli(sol_html, tarih):
        tg = stringWidth(t(tarih), normal, boyut("tarih")) + 8
        tablo = Table([[Paragraph(sol_html, S["unvan"]), Paragraph(t(tarih), S["tarih"])]],
                      colWidths=[genislik - tg, tg])
        tablo.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                   ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                                   ("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
        return tablo

    ust = [Paragraph(t(icerik["name"]), S["isim"])]
    if icerik["headline"]:
        ust.append(Paragraph(t(icerik["headline"]), S["baslik"]))
    ust.append(Paragraph(t(icerik["contact"]), S["iletisim"]))
    if foto:
        # Fotoğraf yalnız geleneksel olduğu ülkelerde ve kişi isterse: sağ üstte, oranı korunur.
        gen, yuk = ImageReader(foto).getSize()
        fy = FOTO_MM[1] * mm
        fg = min(FOTO_MM[0] * mm, fy * gen / yuk)
        fy = fg * yuk / gen
        tablo = Table([[ust, Image(foto, width=fg, height=fy)]], colWidths=[genislik - fg - 8, fg + 8])
        tablo.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                   ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT")]))
        akis = [tablo]
    else:
        akis = ust
    akis += bolum(B["profile"]) + [Paragraph(t(icerik["profile"]), S["govde"])]
    if icerik["skills"]:
        akis += bolum(B["skills"]) + [Paragraph("  ·  ".join(t(s) for s in icerik["skills"]), S["govde"])]
    egitim = bolum(B["education"]) + [Paragraph(t(e), S["satir"]) for e in icerik["education"]]
    if icerik.get("educationFirst"):
        akis += egitim
    if icerik["experience"]:
        akis += bolum(B["experience"])
    for j in icerik["experience"]:
        akis.append(satir_tarihli(t(j["title"]), j["dates"]))
        meta = " · ".join(x for x in (j["org"], j["place"]) if x)
        if meta:
            akis.append(Paragraph(t(meta), S["meta"]))
        if j["ctx"]:
            akis.append(Paragraph(t(j["ctx"]), S["baglam"]))
        akis += [Paragraph(t(m), S["madde"], bulletText="•") for m in j["bullets"]]
        akis.append(Spacer(1, 4 * olcek))
    if icerik["other"]:
        akis += bolum(B["other"])
        for j in icerik["other"]:
            meta = " · ".join(x for x in (j["org"], j["place"]) if x)
            sol = t(j["title"]) + (f'<font name="{normal}" color="#{RENK["gri"]}"> · {t(meta)}</font>' if meta else "")
            akis.append(satir_tarihli(sol, j["dates"]))
            akis += [Paragraph(t(m), S["madde"], bulletText="•") for m in j["bullets"]]
            akis.append(Spacer(1, 2 * olcek))
    if not icerik.get("educationFirst"):
        akis += egitim
    akis += bolum(B["languages"]) + [Paragraph(t(icerik["languages"]), S["satir"])]
    if icerik["itSkills"]:
        akis += bolum(B["it"]) + [Paragraph(t(icerik["itSkills"]), S["satir"])]
    if icerik["projects"]:
        akis += bolum(B["projects"]) + [Paragraph(f"<b>{t(p[0])}</b> – {t(p[1] if len(p) > 1 else '')}", S["satir"])
                                     for p in icerik["projects"]]
    if icerik["gdpr"]:
        akis.append(Paragraph(t(icerik["gdpr"]), S["gdpr"]))

    sayac = {"sayfa": 0}

    def say(_canvas, _doc):
        sayac["sayfa"] += 1

    tampon = io.BytesIO()
    belge = SimpleDocTemplate(tampon, pagesize=A4, leftMargin=KENAR_MM["sol"] * mm, rightMargin=KENAR_MM["sag"] * mm,
                              topMargin=KENAR_MM["ust"] * mm, bottomMargin=KENAR_MM["alt"] * mm,
                              title=f"{icerik['name']} - CV", author=icerik["name"], subject=icerik["headline"])
    belge.build(akis, onFirstPage=say, onLaterPages=say)
    return tampon.getvalue(), sayac["sayfa"]


def _sade(s):
    s = unicodedata.normalize("NFKD", str(s).translate(SADELESTIR))
    return "".join(c for c in s if not unicodedata.combining(c))


def pdf_metin_kontrol(pdf_bytes, icerik, sadelestirildi=False):
    """ATS: PDF'ten metin çıkarılabiliyor mu, isim ve bölüm adları okunuyor mu?"""
    pypdf = paket("pypdf", "pypdf")
    if pypdf is None:
        return [("check", "pypdf kurulamadı: PDF metin okunabilirliği doğrulanamadı")]
    metin = "\n".join((s.extract_text() or "") for s in pypdf.PdfReader(io.BytesIO(pdf_bytes)).pages)
    duz = re.sub(r"\s+", " ", metin)
    isim = _sade(icerik["name"]) if sadelestirildi else icerik["name"]
    B = icerik["basliklar"]
    bolumler = ("profile", "experience", "education") if icerik["experience"] else ("profile", "education")
    beklenen = [isim] + [(_sade(B[k]) if sadelestirildi else B[k]) for k in bolumler]
    eksik = [x for x in beklenen if x not in duz]
    if eksik:
        return [("error", f"PDF metninde okunamayan kısım var: {', '.join(eksik)} (ATS) [C11]")]
    eposta = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", icerik["contact"])
    if eposta and eposta.group(0) not in duz.replace(" ", ""):
        return [("error", "PDF metninde e-posta adresi okunamıyor (ATS) [C11]")]
    return []


# ─── DOCX (python-docx) ─────────────────────────────────────────────────────────

def docx_olustur(docx, icerik, olcek, yol, foto=None):
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Mm, Pt, RGBColor

    B = icerik["basliklar"]
    belge = docx.Document()
    bolum_ayar = belge.sections[0]
    bolum_ayar.page_width, bolum_ayar.page_height = Mm(210), Mm(297)
    bolum_ayar.top_margin, bolum_ayar.bottom_margin = Mm(KENAR_MM["ust"]), Mm(KENAR_MM["alt"])
    bolum_ayar.left_margin, bolum_ayar.right_margin = Mm(KENAR_MM["sol"]), Mm(KENAR_MM["sag"])
    metin_genisligi = Mm(210 - KENAR_MM["sol"] - KENAR_MM["sag"])

    def yazi_tipi_ayarla(stil_ya_da_run):
        rpr = stil_ya_da_run.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.insert(0, rfonts)
        for nitelik in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            rfonts.attrib.pop(qn(nitelik), None)
        for nitelik in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rfonts.set(qn(nitelik), DOCX_YAZI_TIPI)

    def bicim(p, once=0, sonra=0, satir=None):
        pf = p.paragraph_format
        pf.space_before, pf.space_after = Pt(once), Pt(sonra)
        pf.line_spacing = satir or 1.0
        return p

    def yaz(p, metin, anahtar="govde", kalin=False, italik=False, renk_adi="metin"):
        r = p.add_run(str(metin))
        r.font.size = Pt(OLCU[anahtar] * olcek)
        r.font.bold, r.font.italic = kalin, italik
        r.font.color.rgb = RGBColor.from_string(RENK[renk_adi])
        return r

    normal = belge.styles["Normal"]
    yazi_tipi_ayarla(normal)
    normal.font.size = Pt(OLCU["govde"] * olcek)
    normal.font.color.rgb = RGBColor.from_string(RENK["metin"])

    baslik_stili = belge.styles["Heading 1"]
    yazi_tipi_ayarla(baslik_stili)
    baslik_stili.font.size = Pt(OLCU["bolum"] * olcek)
    baslik_stili.font.bold = True
    baslik_stili.font.color.rgb = RGBColor.from_string(RENK["lacivert"])
    baslik_stili.paragraph_format.space_before = Pt(7 * olcek)
    baslik_stili.paragraph_format.space_after = Pt(3 * olcek)
    baslik_stili.paragraph_format.keep_with_next = True
    ppr = baslik_stili.element.get_or_add_pPr()
    kenar = OxmlElement("w:pBdr")
    alt = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", "6"), ("w:space", "1"), ("w:color", RENK["cizgi"])):
        alt.set(qn(k), v)
    kenar.append(alt)
    ppr.append(kenar)

    madde_stili = belge.styles["List Bullet"]
    yazi_tipi_ayarla(madde_stili)
    madde_stili.font.size = Pt(OLCU["govde"] * olcek)

    def bolum(ad):
        p = belge.add_paragraph(style="Heading 1")
        p.add_run(ad)
        return p

    def tarihli_satir(sol_parcalar, tarih):
        p = bicim(belge.add_paragraph())
        p.paragraph_format.tab_stops.add_tab_stop(metin_genisligi, WD_TAB_ALIGNMENT.RIGHT)
        for metin, anahtar, kalin, renk_adi in sol_parcalar:
            yaz(p, metin, anahtar, kalin=kalin, renk_adi=renk_adi)
        yaz(p, "\t" + tarih, "tarih", renk_adi="gri")
        return p

    def madde(metin):
        p = bicim(belge.add_paragraph(style="List Bullet"), sonra=1.4 * olcek)
        p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Mm(4.5), Mm(-3.5)
        yaz(p, metin)

    if foto:
        # Fotoğraflı başlık: kenarlıksız 2 sütunlu tablo (solda ad ve iletişim, sağda fotoğraf).
        tablo = belge.add_table(rows=1, cols=2)
        tablo.autofit = False
        sol, sag = tablo.rows[0].cells
        sol.width, sag.width = Mm(184 - FOTO_MM[0] - 4), Mm(FOTO_MM[0] + 4)
        p = sol.paragraphs[0]
    else:
        sol = None
        p = belge.add_paragraph()
    yaz(bicim(p), icerik["name"], "isim", kalin=True)
    ekle = sol.add_paragraph if sol else belge.add_paragraph
    if icerik["headline"]:
        yaz(bicim(ekle(), 1, 2), icerik["headline"], "baslik", kalin=True, renk_adi="lacivert")
    yaz(bicim(ekle()), icerik["contact"], "iletisim", renk_adi="iletisim")
    if foto:
        fp = bicim(sag.paragraphs[0])
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        fp.add_run().add_picture(foto, height=Mm(FOTO_MM[1]))
    bolum(B["profile"])
    yaz(bicim(belge.add_paragraph(), sonra=3 * olcek, satir=1.05), icerik["profile"])
    if icerik["skills"]:
        bolum(B["skills"])
        yaz(bicim(belge.add_paragraph(), sonra=3 * olcek, satir=1.05), "  ·  ".join(icerik["skills"]))
    def egitim():
        bolum(B["education"])
        for e in icerik["education"]:
            yaz(bicim(belge.add_paragraph(), sonra=2 * olcek), e)

    if icerik.get("educationFirst"):
        egitim()
    if icerik["experience"]:
        bolum(B["experience"])
    for j in icerik["experience"]:
        tarihli_satir([(j["title"], "unvan", True, "metin")], j["dates"])
        meta = " · ".join(x for x in (j["org"], j["place"]) if x)
        if meta:
            yaz(bicim(belge.add_paragraph()), meta, "meta", renk_adi="gri")
        if j["ctx"]:
            yaz(bicim(belge.add_paragraph()), j["ctx"], "baglam", italik=True, renk_adi="acik_gri")
        for m in j["bullets"]:
            madde(m)
        belge.paragraphs[-1].paragraph_format.space_after = Pt(4 * olcek)
    if icerik["other"]:
        bolum(B["other"])
        for j in icerik["other"]:
            meta = " · ".join(x for x in (j["org"], j["place"]) if x)
            tarihli_satir([(j["title"], "unvan", True, "metin")] + ([(" · " + meta, "meta", False, "gri")] if meta else []),
                          j["dates"])
            for m in j["bullets"]:
                madde(m)
    if not icerik.get("educationFirst"):
        egitim()
    bolum(B["languages"])
    yaz(bicim(belge.add_paragraph(), sonra=2 * olcek), icerik["languages"])
    if icerik["itSkills"]:
        bolum(B["it"])
        yaz(bicim(belge.add_paragraph(), sonra=2 * olcek), icerik["itSkills"])
    if icerik["projects"]:
        bolum(B["projects"])
        for pr in icerik["projects"]:
            p = bicim(belge.add_paragraph(), sonra=2 * olcek)
            yaz(p, pr[0], kalin=True)
            yaz(p, " – " + (pr[1] if len(pr) > 1 else ""))
    if icerik["gdpr"]:
        yaz(bicim(belge.add_paragraph(), once=6 * olcek), icerik["gdpr"], "gdpr", italik=True, renk_adi="gdpr")

    cp = belge.core_properties
    cp.author = cp.last_modified_by = icerik["name"]
    cp.title, cp.subject, cp.comments, cp.keywords = f"{icerik['name']} - CV", icerik["headline"], "", ""
    belge.save(yol)


def on_yazi_docx(docx, metin, ad, yol):
    from docx.shared import Pt
    belge = docx.Document()
    belge.styles["Normal"].font.name = DOCX_YAZI_TIPI
    belge.styles["Normal"].font.size = Pt(11)
    for paragraf in re.split(r"\n\s*\n", metin.strip()):
        belge.add_paragraph(paragraf.strip())
    cp = belge.core_properties
    cp.author = cp.last_modified_by = ad
    cp.title, cp.comments = f"{ad} - Cover Letter", ""
    belge.save(yol)


# ─── ana akış ──────────────────────────────────────────────────────────────────

def _calistir(a):
    try:
        P = kontrol.oku_json(a.profil)
        J = kontrol.oku_json(a.ilan) if a.ilan else {}
    except kontrol.GirdiHatasi as e:
        print(f"  HATA    dosya: {e}")
        return 2

    # Şema bozuksa (yanlış tür, eksik zorunlu alan) çıkış 2; bilinmeyen anahtar ya da unvan değişikliği 1.
    # İkisinde de dosya üretilmez.
    sema = [b for b in kontrol.profil_yapisi(P) + kontrol.ilan_yapisi(J) if b[0] == "error"]
    icerik_hatasi = [] if sema else [b for b in kontrol.cv_icerigi(P, J)[1] if b[0] == "error"]
    if sema or icerik_hatasi:
        kontrol.rapor("Yapı" if sema else "CV", sema or icerik_hatasi)
        print(kontrol.sonuc_satiri(True, len(sema or icerik_hatasi)))
        return 2 if sema else 1

    cikti = a.cikti or (os.path.join("cikti", dosya_adi(J.get("company") or "ilan")) if a.ilan else "cikti")
    ad = dosya_adi(P.get("name", "CV"))
    # Dosya adı iş ailesine göre (CV başka şirketlere iletilebilir; şirket adı dosya adında olmaz).
    ek = f"_{dosya_adi(J['family'])}" if J.get("family") else ""
    icerik, bulgular = kontrol.cv_kontrol(P, J)
    if a.foto and not os.path.isfile(a.foto):
        print(f"  HATA    dosya: fotoğraf bulunamadı: {a.foto}")
        return 2

    # Önce her şey bellekte üretilir; yalnız kontrol temizse diske yazılır (hatalı CV indirilebilir yere düşmez).
    uretilen = {}
    olcek, sayfa, sinir = 1.0, 0, icerik["sayfa"]
    reportlab = paket("reportlab", "reportlab")
    if reportlab is None:
        bulgular.append(("error", "reportlab kurulamadı: PDF üretilemedi (internet erişimi kapalı olabilir)"))
    else:
        if a.foto and paket("PIL", "pillow") is None:
            bulgular.append(("error", "pillow kurulamadı: fotoğraf eklenemedi"))
        yazi_tipi = pdf_yazi_tipi(a.yazi_tipi)
        if yazi_tipi[3]:
            bulgular.append(("check", "Unicode yazı tipi bulunamadı: PDF'te özel harfler sadeleştirildi (Ł yerine L)"))
        for olcek in OLCEKLER:
            pdf, sayfa = pdf_olustur(icerik, olcek, yazi_tipi, a.foto)
            if sayfa <= sinir:
                break
        if sayfa > sinir:
            bulgular.append(("error", f"CV {sayfa} sayfa, sınır {sinir}: madde azalt ya da Other Experience'ı "
                                      f"kısalt (ülke 2 sayfaya izin veriyorsa cvPages: 2) [C11]"))
        elif olcek < 1:
            bulgular.append(("check", f"sığdırmak için yazı %{round(olcek * 100)} boyuta küçültüldü"))
        bulgular += pdf_metin_kontrol(pdf, icerik, yazi_tipi[3])
        uretilen[f"{ad}_CV{ek}.pdf"] = pdf

    docx = paket("docx", "python-docx")
    if docx is None:
        bulgular.append(("error", "python-docx kurulamadı: Word dosyası üretilemedi"))
    else:
        tampon = io.BytesIO()
        docx_olustur(docx, icerik, olcek, tampon, a.foto)
        uretilen[f"{ad}_CV{ek}.docx"] = tampon.getvalue()

    hatali = kontrol.rapor("CV", bulgular)
    sayi = len(bulgular)
    if J.get("coverLetter"):
        b = kontrol.metin_kontrol(J["coverLetter"], P, J)
        hatali = kontrol.rapor("Ön yazı", b) or hatali
        sayi += len(b)
        uretilen[f"{ad}_Cover_Letter{ek}.txt"] =(J["coverLetter"].strip() + "\n").encode("utf-8")
        if docx is not None:
            tampon = io.BytesIO()
            on_yazi_docx(docx, J["coverLetter"], icerik["name"], tampon)
            uretilen[f"{ad}_Cover_Letter{ek}.docx"] = tampon.getvalue()

    if hatali:
        print("  dosya: yazılmadı (önce HATA satırlarını düzelt, sonra yeniden çalıştır)")
    else:
        os.makedirs(cikti, exist_ok=True)
        for dosya, veri in uretilen.items():
            yol = os.path.join(cikti, dosya)
            with open(yol, "wb") as f:
                f.write(veri)
            print(f"  dosya: {yol}" + (f" ({sayfa} sayfa)" if dosya.endswith(".pdf") else ""))
    if J.get("company"):
        print(f"  ilan: {J.get('company')} / {J.get('role', '')}")
    print(kontrol.sonuc_satiri(hatali, sayi))
    return 1 if hatali else 0


def main(argv=None):
    kontrol.utf8_cikis()
    ap = argparse.ArgumentParser(description="Profil + ilan seçiminden tek sayfa CV (DOCX + PDF) üretir")
    ap.add_argument("--profile", "--profil", dest="profil", required=True, help="kişinin profile.json dosyası")
    ap.add_argument("--job", "--ilan", dest="ilan", help="ilana özel seçim (job.json)")
    ap.add_argument("--out", "--cikti", dest="cikti", help="çıktı klasörü; kişinin indirebileceği yer (claude.ai'de genelde "
                                    "/mnt/user-data/outputs/<sirket>)")
    ap.add_argument("--photo", "--foto", dest="foto", help="isteğe bağlı vesikalık fotoğraf (jpg/png); yalnız fotoğrafın gelenek olduğu "
                                   "ülkelerde ve kişi isterse")
    ap.add_argument("--font", "--yazi-tipi", dest="yazi_tipi", default="auto", choices=["auto", "liberation", "arial", "dejavu", "helvetica"],
                    help="PDF yazı tipi (test için; normalde auto)")
    a = ap.parse_args(argv)
    try:
        return _calistir(a)
    except Exception as e:  # program hatası: HATA (1) ile karışmasın
        print(f"  HATA    program: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
