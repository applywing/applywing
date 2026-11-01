#!/usr/bin/env python3
"""tracker.py: başvuru takip tablosu (tracker.xlsx): ekle / güncelle / bul / listele / özet / takip / analiz.

Bağımlılık: openpyxl (yoksa otomatik `pip install` denenir). Tablo yoksa assets/tracker-template.xlsx'ten
kopyalanır. Sütunlar konumla okunur (A-Q); başlıklar kişinin diline çevrilmiş olabilir.

Kullanım (<skill> = bu skill'in klasörü; --file iş klasöründeki tablo):
  python <skill>/scripts/tracker.py --file tracker.xlsx add --company X --position Y [--city ..] [--channel ..]
         [--link ..] [--fit ..] [--decision ..] [--cv ..] [--status ..] [--note ..] [--family ..] [--via ..]
         [--date YYYY-MM-DD]
      aynı link ya da aynı şirket + pozisyon varsa yeni satır açmaz, o satırı günceller
      --family: iş ailesi (ör. "customer support", "purchasing") · --via: başvuru yolu (ör. Workday,
      Easy Apply, company form, email, agency) · --date: başvuru günü bugün değilse ("dün gönderdim")
  python <skill>/scripts/tracker.py --file tracker.xlsx update --no 3 [--status ..] [--note ".."] [--followup]
         [--reply-date YYYY-MM-DD] [--date YYYY-MM-DD]
      ret / mülakat / test / teklif durumuna geçince cevap tarihi (Q) boşsa bugün yazılır
      --date: başvuru tarihini (B) düzeltir, ör. "Prepared" satırı gönderilince gönderim günü
  python <skill>/scripts/tracker.py --file tracker.xlsx find [--link ..] [--company .. --position ..]
  python <skill>/scripts/tracker.py --file tracker.xlsx list [--status Sent]
  python <skill>/scripts/tracker.py --file tracker.xlsx summary [--days 7]
  python <skill>/scripts/tracker.py --file tracker.xlsx due [--days 10]
      "Sent" durumunda, son hareketten bu yana N gün geçmiş ve takip maili önerilmemiş başvurular
  python <skill>/scripts/tracker.py --file tracker.xlsx analyze [--min 5]
      neden ret geliyor, nereye odaklanmalı: kanal / iş ailesi / başvuru yolu / uyum seviyesine göre cevap
      oranı, hızlı retler (2 gün içinde: çoğu zaman otomatik eleme), cevap süresi, sinyal vermeyenler

Çıkış kodu: 0 = tamam · 2 = dosya ya da kullanım sorunu.
"""

import argparse
import datetime as dt
import importlib
import os
import shutil
import statistics
import subprocess
import sys

SUTUN = {"no": 1, "date": 2, "company": 3, "position": 4, "city": 5, "channel": 6, "link": 7, "fit": 8,
         "decision": 9, "cv": 10, "status": 11, "last": 12, "followup": 13, "note": 14, "family": 15,
         "via": 16, "reply": 17}
BASLIK_EK = {15: "Role family", 16: "Applied via", 17: "Reply date"}
SABLON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "tracker-template.xlsx")
# Durum kelimeleri kişinin dilinde olabilir; sık dillerdeki karşılıklar tanınır.
GONDERILDI = {"sent", "gönderildi", "gesendet", "wysłane", "enviado", "envoyé", "inviato", "verzonden"}
GORULDU = {"viewed", "görüntülendi", "gesehen", "wyświetlone", "visto", "vu", "bekeken"}
RET = {"rejected", "ret", "reddedildi", "abgelehnt", "odrzucone", "rechazado", "rejeté", "rifiutato",
       "afgewezen"}
OLUMLU = {"interview", "mülakat", "test", "offer", "teklif", "vorstellungsgespräch", "rozmowa", "oferta",
          "entrevista", "entretien", "offre", "colloquio", "gesprek", "aanbod"}
HAZIRLIK = {"", "prepared", "hazırlandı", "vorbereitet", "przygotowane", "preparado", "préparé", "preparato",
            "voorbereid"}
BASVURULMADI = {"skip", "seen", "başvurma", "bakıldı", "maybe", "belki"}


def openpyxl_yukle():
    try:
        return importlib.import_module("openpyxl")
    except ImportError:
        pass
    for ek in ([], ["--break-system-packages"], ["--user"]):
        if subprocess.run([sys.executable, "-m", "pip", "install", "-q", "openpyxl", *ek],
                          capture_output=True).returncode == 0:
            importlib.invalidate_caches()
            try:
                return importlib.import_module("openpyxl")
            except ImportError:
                continue
    return None


def bugun():
    return dt.date.today().isoformat()


def satirlar(ws):
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, SUTUN["company"]).value or ws.cell(r, SUTUN["link"]).value:
            yield r


def deger(ws, r, ad):
    v = ws.cell(r, SUTUN[ad]).value
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()[:10]
    return "" if v is None else str(v)


def durum(ws, r):
    return deger(ws, r, "status").strip().lower()


def ayni_mi(ws, r, link, sirket, pozisyon):
    # İki kaydın da bağlantısı varsa yalnız bağlantı karşılaştırılır: aynı şirketin farklı şehirdeki aynı
    # pozisyonu ayrı ilandır. Bağlantı yoksa şirket + pozisyon.
    eski_link = deger(ws, r, "link").strip().rstrip("/")
    if link and eski_link:
        return eski_link == link.strip().rstrip("/")
    return bool(sirket and pozisyon and deger(ws, r, "company").strip().lower() == sirket.strip().lower()
                and deger(ws, r, "position").strip().lower() == pozisyon.strip().lower())


def yaz_satir(ws, r):
    alanlar = ["no", "date", "company", "position", "city", "channel", "family", "via", "fit", "decision",
               "status", "last", "reply", "followup", "link", "cv", "note"]
    print("  " + " | ".join(f"{a}={deger(ws, r, a)}" for a in alanlar if deger(ws, r, a)))


def tarih(s):
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def basliklari_tamamla(ws):
    """Eski tablolarda (A-N) yeni sütun başlıklarını ekler."""
    for sutun, ad in BASLIK_EK.items():
        if not ws.cell(1, sutun).value:
            ws.cell(1, sutun).value = ad


def basvuruldu_mu(ws, r):
    return (durum(ws, r) not in HAZIRLIK
            and deger(ws, r, "decision").strip().lower() not in BASVURULMADI)


def analiz(ws, en_az):
    basvurular = [r for r in satirlar(ws) if basvuruldu_mu(ws, r)]
    if not basvurular:
        print("  Henüz gönderilmiş başvuru yok.")
        return

    def bilgi(r):
        d = durum(ws, r)
        gonderim, cevap = tarih(deger(ws, r, "date")), tarih(deger(ws, r, "reply"))
        gun = (cevap - gonderim).days if gonderim and cevap else None
        return {"cevap": d in RET or d in OLUMLU or cevap is not None, "olumlu": d in OLUMLU, "ret": d in RET,
                "hizli_ret": d in RET and gun is not None and gun <= 2, "goruldu": d in GORULDU, "gun": gun,
                "bekliyor": d in GONDERILDI | GORULDU and gonderim and (dt.date.today() - gonderim).days > 14}

    veriler = {r: bilgi(r) for r in basvurular}
    n = len(basvurular)
    cevap = sum(v["cevap"] for v in veriler.values())
    olumlu = sum(v["olumlu"] for v in veriler.values())
    gunler = [v["gun"] for v in veriler.values() if v["gun"] is not None]
    print(f"  GENEL: {n} başvuru · cevap {cevap} (%{round(100 * cevap / n)}) · olumlu (mülakat/test/teklif) "
          f"{olumlu} · ret {sum(v['ret'] for v in veriler.values())} · hızlı ret (≤2 gün) "
          f"{sum(v['hizli_ret'] for v in veriler.values())} · 14+ gündür sessiz "
          f"{sum(bool(v['bekliyor']) for v in veriler.values())}"
          + (f" · ortalama cevap süresi {round(statistics.mean(gunler))} gün" if gunler else ""))

    isaretler = []
    for boyut, ad, kucuk in (("channel", "KANAL", "kanal"), ("family", "İŞ AİLESİ", "iş ailesi"),
                             ("via", "BAŞVURU YOLU", "başvuru yolu"), ("fit", "UYUM", "uyum")):
        gruplar = {}
        for r in basvurular:
            gruplar.setdefault(deger(ws, r, boyut).strip() or "-", []).append(veriler[r])
        print(f"  {ad}:")
        for anahtar, liste in sorted(gruplar.items(), key=lambda x: -len(x[1])):
            k = len(liste)
            c = sum(v["cevap"] for v in liste)
            o = sum(v["olumlu"] for v in liste)
            h = sum(v["hizli_ret"] for v in liste)
            print(f"    {anahtar}: {k} başvuru · cevap {c} · olumlu {o} · hızlı ret {h}")
            if anahtar == "-":
                continue
            if k >= en_az and c == 0:
                isaretler.append(f"{kucuk} '{anahtar}': {k} başvuruda hiç cevap yok")
            if h >= 3 and h >= k / 2:
                isaretler.append(f"{kucuk} '{anahtar}': {h}/{k} hızlı ret (otomatik eleme olabilir: izin, dil, "
                                 f"eleme soruları)")
            if k >= 3 and o >= 1 and o / k >= max(0.2, 1.5 * olumlu / n):
                isaretler.append(f"{kucuk} '{anahtar}': olumlu dönüş oranı ortalamanın üstünde ({o}/{k})")
    goruldu_sessiz = sum(v["goruldu"] for v in veriler.values())
    if goruldu_sessiz >= 3:
        isaretler.append(f"{goruldu_sessiz} başvuru görüntülendi ama cevap yok: CV'nin ilk 6 saniyesi (başlık, profil) "
                         f"ilana yeterince uymuyor olabilir")
    print("  İŞARETLER: " + ("; ".join(isaretler) if isaretler else "henüz belirgin bir örüntü yok (az veri)"))
    if n < 15:
        print(f"  NOT: {n} başvuru az veri; sonuçları kesin yargı gibi sunma.")


def main(argv=None):
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Başvuru takip tablosu")
    ap.add_argument("--file", required=True, help="tracker.xlsx (iş klasöründe)")
    alt = ap.add_subparsers(dest="komut", required=True)
    ekle = alt.add_parser("add")
    for ad in ("company", "position", "city", "channel", "link", "fit", "decision", "cv", "status", "note",
               "family", "via"):
        ekle.add_argument(f"--{ad}", default="")
    ekle.add_argument("--date", default="", help="başvuru günü (YYYY-MM-DD), bugün değilse")
    gun = alt.add_parser("update")
    gun.add_argument("--no", type=int, required=True)
    for ad in ("status", "note", "fit", "decision", "cv", "link", "family", "via"):
        gun.add_argument(f"--{ad}")
    gun.add_argument("--date", help="başvuru tarihini düzelt (YYYY-MM-DD)")
    gun.add_argument("--reply-date", dest="reply_date", help="cevabın geldiği gün (YYYY-MM-DD)")
    gun.add_argument("--followup", action="store_true", help="takip maili önerildi: bugünün tarihini yaz")
    bul = alt.add_parser("find")
    for ad in ("link", "company", "position"):
        bul.add_argument(f"--{ad}", default="")
    lst = alt.add_parser("list")
    lst.add_argument("--status")
    oz = alt.add_parser("summary")
    oz.add_argument("--days", type=int, default=7)
    vade = alt.add_parser("due")
    vade.add_argument("--days", type=int, default=10)
    an = alt.add_parser("analyze")
    an.add_argument("--min", type=int, default=5, help="'sinyal yok' demek için en az başvuru sayısı")
    a = ap.parse_args(argv)

    openpyxl = openpyxl_yukle()
    if openpyxl is None:
        print("  HATA    openpyxl kurulamadı (internet erişimi olmayabilir)")
        return 2
    if not os.path.exists(a.file):
        if a.komut != "add":
            print(f"  Tablo yok: {a.file} (ilk 'add' ile oluşur)")
            return 0
        os.makedirs(os.path.dirname(os.path.abspath(a.file)), exist_ok=True)
        shutil.copy2(SABLON, a.file)
    try:
        wb = openpyxl.load_workbook(a.file)
    except Exception as e:  # açık Excel dosyası, bozuk dosya
        print(f"  HATA    dosya açılamadı: {e} (Excel'de açıksa kapat)")
        return 2
    ws = wb.worksheets[0]

    for t in (getattr(a, "date", None), getattr(a, "reply_date", None)):
        if t and tarih(t) is None:
            print(f"  HATA    tarih YYYY-MM-DD olmalı: {t}")
            return 2

    if a.komut == "add":
        basliklari_tamamla(ws)
        hedef = next((r for r in satirlar(ws) if ayni_mi(ws, r, a.link, a.company, a.position)), None)
        yeni = hedef is None
        if yeni:
            hedef = max(list(satirlar(ws)) or [1]) + 1
            no = max([int(deger(ws, r, "no") or 0) for r in satirlar(ws) if deger(ws, r, "no").isdigit()] or [0]) + 1
            ws.cell(hedef, SUTUN["no"]).value = no
            ws.cell(hedef, SUTUN["date"]).value = a.date or bugun()
        elif a.date:
            ws.cell(hedef, SUTUN["date"]).value = a.date
        for ad in ("company", "position", "city", "channel", "link", "fit", "decision", "cv", "status", "family",
                   "via"):
            v = getattr(a, ad)
            # Var olan satırda şirket ve pozisyonun yazımı korunur; yalnız boşsa doldurulur.
            if v and (yeni or ad not in ("company", "position") or not deger(ws, hedef, ad)):
                ws.cell(hedef, SUTUN[ad]).value = v
        ws.cell(hedef, SUTUN["last"]).value = f"{a.date or bugun()} {a.status or ''}".strip()
        if a.note:
            ws.cell(hedef, SUTUN["note"]).value = a.note
        print(f"  {'eklendi' if yeni else 'zaten vardı, güncellendi'}: No {deger(ws, hedef, 'no')}")
        yaz_satir(ws, hedef)
    elif a.komut == "update":
        basliklari_tamamla(ws)
        hedef = next((r for r in satirlar(ws) if deger(ws, r, "no") == str(a.no)), None)
        if hedef is None:
            print(f"  HATA    No {a.no} bulunamadı")
            return 2
        for ad in ("status", "fit", "decision", "cv", "link", "family", "via"):
            v = getattr(a, ad)
            if v:
                ws.cell(hedef, SUTUN[ad]).value = v
        if a.date:
            ws.cell(hedef, SUTUN["date"]).value = a.date
        if a.reply_date:
            ws.cell(hedef, SUTUN["reply"]).value = a.reply_date
        elif a.status and a.status.strip().lower() in RET | OLUMLU and not deger(ws, hedef, "reply"):
            ws.cell(hedef, SUTUN["reply"]).value = bugun()
        if a.status or a.note:
            ws.cell(hedef, SUTUN["last"]).value = f"{a.reply_date or a.date or bugun()} {a.note or a.status}".strip()
        if a.followup:
            ws.cell(hedef, SUTUN["followup"]).value = bugun()
        print("  güncellendi:")
        yaz_satir(ws, hedef)
    elif a.komut == "find":
        bulunan = [r for r in satirlar(ws) if ayni_mi(ws, r, a.link, a.company, a.position)]
        print(f"  {len(bulunan)} eşleşme")
        for r in bulunan:
            yaz_satir(ws, r)
        return 0
    elif a.komut == "list":
        for r in satirlar(ws):
            if not a.status or durum(ws, r) == a.status.lower():
                yaz_satir(ws, r)
        return 0
    elif a.komut == "summary":
        # Bugün dahil son N takvim günü; bir önceki N gün de karşılaştırma için sayılır.
        sinir = dt.date.today() - dt.timedelta(days=a.days - 1)
        onceki = sinir - dt.timedelta(days=a.days)
        tum, son, once, cevaplar, kanallar = {}, {}, {}, {}, {}
        for r in satirlar(ws):
            d = deger(ws, r, "status") or "-"
            tum[d] = tum.get(d, 0) + 1
            t = tarih(deger(ws, r, "date"))
            if t and t >= sinir:
                son[d] = son.get(d, 0) + 1
            elif t and t >= onceki:
                once[d] = once.get(d, 0) + 1
            c = tarih(deger(ws, r, "reply"))
            if c and c >= sinir:
                cevaplar[d] = cevaplar.get(d, 0) + 1
            k = deger(ws, r, "channel") or "-"
            kanallar.setdefault(k, {}).setdefault(d, 0)
            kanallar[k][d] += 1
        print(f"  son {a.days} gün (başvuru tarihine göre): "
              + (" · ".join(f"{k} {v}" for k, v in son.items()) or "yok"))
        print(f"  ondan önceki {a.days} gün: " + (" · ".join(f"{k} {v}" for k, v in once.items()) or "yok"))
        print(f"  son {a.days} günde gelen cevaplar (cevap tarihine göre): "
              + (" · ".join(f"{k} {v}" for k, v in cevaplar.items()) or "yok"))
        print("  toplam: " + (" · ".join(f"{k} {v}" for k, v in tum.items()) or "yok"))
        for k, d in kanallar.items():
            print(f"  kanal {k}: " + " · ".join(f"{s} {n}" for s, n in d.items()))
        return 0
    elif a.komut == "due":
        sinir = dt.date.today() - dt.timedelta(days=a.days)
        bulunan = []
        for r in satirlar(ws):
            if durum(ws, r) not in GONDERILDI or deger(ws, r, "followup"):
                continue
            t = tarih(deger(ws, r, "last")) or tarih(deger(ws, r, "date"))
            if t and t <= sinir:
                bulunan.append(r)
        print(f"  takip zamanı gelen: {len(bulunan)}")
        for r in bulunan:
            yaz_satir(ws, r)
        return 0
    elif a.komut == "analyze":
        analiz(ws, a.min)
        return 0

    try:
        wb.save(a.file)
    except PermissionError:
        print("  HATA    kaydedilemedi: tablo Excel'de açık olabilir, kapatıp yeniden dene")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
