<!-- Example of assistant output in the person's language (Turkish here). Fit labels are the Turkish versions of Strong fit / Good fit. -->

# Örnek: ilan avı sonucu ve ilan değerlendirmesi (KURGUSAL)

Kişi: Ece Yildirim (`profile-en.json`). Kesin elemeleri (profil belgesinden): Lehçe isteyen ya da Lehçe
yazılmış ilan · gece vardiyası · Varşova dışı ofis zorunluluğu (tam uzaktan hariç). Maaş tabanı
5,800 PLN brüt. Çalışma izni: oturma kartı, iş piyasasına serbest erişim (sponsorluk gerekmez).

Kaynak: `linkedin-alert-email.txt` (Kaynak A) + takip tablosu `tracker-example.csv`.

---

## İlan avı özeti (asistanın kişiye yazdığı)

> 6 ilan baktım. **3'ü elendi:** 1 Lehçe ilan (unvan Lehçe), 1 gece vardiyası, 1 şüpheli ilan.
> ⚠️ Şüpheli olan "Remote Data Entry… 3000 EUR per week, contact us on Telegram": haftalık abartılı kazanç
> ve Telegram'a çağırma dolandırıcılık işareti. Başka yerde görürsen de başvurma.
> 1 ilan zaten tablonda var (Example Retail Group, 22 Ekim'de gönderildi), atladım.
>
> **Sana uygun 2 ilan:**
>
> 1. Customer Support Specialist with Turkish · Bluewave Travel Services · Varşova (hibrit) · 6,000–7,500 PLN brüt · 3 gün önce
>    Uyum: Çok uygun · Bağlantı: seyahat acentesinde 3 yıl Türkçe/İngilizce müşteri desteği → aynı iş · Not: vardiya 8:00–20:00 (gece yok)
>    Kaynak: LinkedIn bildirimi · linkedin.com/jobs/view/4100000001
> 2. Junior Purchasing Assistant · Vistula Parts Distribution · Varşova (ofis) · maaş yazmıyor · 5 gün önce
>    Uyum: Uygun · Bağlantı: mobilya ithalatçısında satın alma siparişi ve tedarikçi faturası → satın alma · Not: ⚠️ SAP "artı"
>    Kaynak: LinkedIn bildirimi · linkedin.com/jobs/view/4100000002
>
> Hangilerine bakalım? Numarasını yazman yeter.

(Linkler maildeki takip linkinden değil, ilan numarasıyla sitenin herkese açık adresinden açılır.)

---

## 1. Customer Support Specialist with Turkish · Bluewave Travel Services · Varşova (hibrit)

**Uyum:** Çok uygun · **Öğrenmesi:** Kolay
İlk gün: Türkçe ve İngilizce müşteri yazışması, vaka kaydı, iade/rezervasyon değişikliği talepleri.
2–8 haftada: şirketin rezervasyon sistemi ve iç kuralları (ilan eğitim veriyor).

**Şartlar**
- ✅ Akıcı Türkçe + İngilizce B2: Türkçe ana dil, İngilizce B2
- ✅ En az 1 yıl müşteri hizmetleri: seyahat acentesinde 06/2019–08/2022
- ✅ Ticketing aracı (Zendesk) artı: Zendesk'te vaka kaydı ve takibi (profilde var)
- ✅ 8:00–20:00 vardiya, hafta içi: kesin elemelerle çelişmiyor
- ❌ Yapısal engel: yok (Lehçe gerekmiyor, izin uygun)

**Karar:** Başvur. İşin günlük görevleri kişinin seyahat acentesindeki işiyle birebir örtüşüyor.

**CV planı:** başlık `Customer Support Specialist | Turkish & English`. Öne çıkacak maddeler:
`travel.calls`, `travel.zendesk`, `travel.refunds`, `travel.complaints`, sonra `furniture.customers`.
Bağlantı: Türkçe/İngilizce müşteri desteği → aynı rol. (`job-1-selection.json`)

**Riskler:** abartı riski yok. Ön yazıda yalnız profildeki rakam (40 çağrı/mail) kullanıldı. İzin:
ilan "geçerli oturma kartı olan adaylara destek" diyor, kişinin durumuyla uyumlu.

---

## 2. Junior Purchasing Assistant · Vistula Parts Distribution · Varşova (ofis)

**Uyum:** Uygun · **Öğrenmesi:** Kolay
İlk gün: satın alma siparişi oluşturma ve gönderme, teslimat takibi, Excel kayıtları, tedarikçiyle
İngilizce/Türkçe yazışma.
2–8 haftada: SAP MM'de sipariş ve fatura eşleştirme (ilan "eğitim veririz" diyor), sektör terminolojisi.

**Şartlar**
- ✅ 1–2 yıl satın alma/sipariş yönetimi: 09/2022–03/2024 sipariş ve teslimat yönetimi (18 ay)
- ✅ İngilizce B2+: B2
- ✅ Türkçe artı: ana dil; ekip Türkiye'deki tedarikçilerle çalışıyor
- ⚠️ "Good knowledge of Excel": filtre, VLOOKUP, temel pivot var. CV'de seviye değil yapılan iş yazılır.
- ⚠️ SAP MM artı: kullanmadı; öğrenilebilir, ilan eğitim veriyor. CV'de ve ön yazıda **yazılmaz**.
- ⚠️ "Goods receipt" ile eşleştirme: siparişle fatura kontrolü yaptı; depo giriş kaydı tarafı yeni.
- ❌ Yapısal engel: yok

**Karar:** Başvuru yapılabilir; sipariş ve tedarikçi faturası deneyimi güçlü bir köprü, eksikler
öğrenilebilir sistem bilgisi.

**CV planı:** başlık `Purchase Orders & Supplier Administration | English & Turkish`. Önce
`furniture` işi (orders, invoices, log, customers), sonra `travel` (calls, refunds). Köprü: satın alma
siparişi + fatura kontrolü → satın alma asistanı. (`job-2-selection.json`)

**Riskler:** "Good knowledge of Excel" formda sorulursa orta seviye seçilir; mülakatta canlı Excel
testi olabilir (`interview.md` F3). SAP sorulursa dürüst cevap: kullanmadım + sipariş/fatura deneyimi.
Maaş yazmıyor; formda profildeki rakam söylenir.

---

Üretilen dosyalar: `output/job-1-bluewave/`, `output/job-2-vistula/` (CV PDF + Word, ön yazı).
Kontrol sonucu: ikisi de temiz.
