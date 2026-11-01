# Countries: CV customs and job sites

**Open when:** setup Part 1 (target countries, which sites), before the first CV for a new country,
when the person picks a job in another country.

These are **general tendencies, not laws**. The job ad always wins ("send a CV without photo", "in
German", "max 2 pages"). If a country isn't listed, web-search "<country> CV format" and "most used job
sites <country>" and summarise for the person in two sentences. Re-check with a quick search if
something looks outdated; job sites change.

## How the CV adapts (fields in cv-data.json / the job's json)

| Field | Meaning |
|---|---|
| `cvLanguage` | Language of the CV data file (en, de, tr, pl, fr, es, it, nl, pt have built-in section headings; other languages: add `headings`) |
| `cvPages` | Page limit 1–3 (the script shrinks text slightly, then fails if still longer) |
| `country` | Country of the job (in job.json) or default target (profile). PL and IT get a data-processing consent line automatically |
| `futureRecruitment` | `true` only if the person wants their data kept for future recruitment; then the Polish line covers that too. Default `false` (this recruitment only) |
| `gdpr` | Custom consent line, or `""` to suppress it |
| `--photo` | Only where photos are customary **and** the person wants one; otherwise never |

One person applying in two languages needs two approved CV data files, `cv-data.json` and `cv-data-<lang>.json` (e.g. English for international
roles, German for local German ads). Translate faithfully; titles may be translated but not upgraded.
Show the translated lines for approval like any other line.

## CV customs by country (general tendency)

| Country | Name / pages | Photo | Personal details | Extras |
|---|---|---|---|---|
| USA, Canada | "Resume", 1 page (2 for long careers) | No | No age, birth date, marital status, nationality | Cover letter often optional; achievements with numbers |
| UK, Ireland | "CV", 2 pages common | No | No birth date, photo or marital status | Cover letter valued; no "References available on request" needed |
| Australia, New Zealand | 2–3 pages | No | Minimal | Referees often listed at the end |
| Germany, Austria, Switzerland | "Lebenslauf", 1–2 pages, reverse chronological | Common but optional | Birth date optional | Cover letter (Anschreiben) still expected by many; certificates (Zeugnisse) asked often |
| Netherlands, Belgium | 1–2 pages | Optional | Minimal | Short motivation letter common |
| Nordics | 1–2 pages | Optional, fairly common | Minimal | Personal letter (personligt brev) common in Sweden |
| France | 1 page typical | Optional (was common) | Minimal | "Lettre de motivation" common |
| Spain, Portugal | 1–2 pages | Common | Sometimes birth date | Cover letter less central |
| Italy | 1–2 pages | Common | Sometimes birth date | **GDPR consent line expected** (auto) |
| Poland | 1–2 pages | Optional | Minimal | **GDPR/RODO consent line expected** (auto) |
| Czechia, Slovakia, Hungary, Romania | 1–2 pages | Common | Minimal | Some ads ask for a consent line: add via `gdpr` |
| Turkey | 1–2 pages | Very common | Birth date common (optional: the person adds it to the Word file themselves; never ask for it); military service status often asked for men | Local sites ask for full profiles |
| UAE, Saudi Arabia, Qatar, Gulf | 2 pages | Common | Nationality and visa status commonly stated | Notice period and visa status matter a lot |
| India | 1–2 pages | Rare | Minimal | Notice period often asked |
| Japan | Fixed formats (rirekisho) | Yes | Many | Advise the person to use the official form; this script's layout is not the standard |

## Job sites by country (suggest 3–5, the person chooses)

Always relevant: **LinkedIn** (alerts by email), **Indeed** (most countries, alerts by email),
company career pages. Remote work: We Work Remotely, Remote OK, Remotive.

| Country | Popular sites |
|---|---|
| Poland | pracuj.pl (biggest general site), rocketjobs.pl (office, sales, customer service), OLX Praca (local, hourly jobs), justjoin.it · theprotocol.it · nofluffjobs.com (mainly IT) |
| Germany | StepStone (biggest general site), Bundesagentur für Arbeit Jobbörse (public service), XING (professional network), Indeed, Arbeitnow (English-language jobs, many in tech) |
| Austria / Switzerland | karriere.at, AMS eJob-Room / jobs.ch, jobup.ch |
| Netherlands | Nationale Vacaturebank, Indeed, LinkedIn; agencies for English-speaking roles |
| Belgium | StepStone.be, VDAB / Actiris / Le Forem (public), Jobat |
| UK | Reed, Totaljobs, CV-Library, Indeed, gov.uk "Find a job" |
| Ireland | IrishJobs.ie, Jobs.ie, Indeed |
| France | France Travail, APEC (managers), Welcome to the Jungle, HelloWork, Indeed |
| Spain | InfoJobs, InfoEmpleo, Indeed, LinkedIn |
| Portugal | Net-Empregos, Indeed, ITJobs.pt (IT) |
| Italy | InfoJobs.it, Indeed, LinkedIn |
| Sweden / Denmark / Norway / Finland | Platsbanken (Arbetsförmedlingen) / Jobindex / FINN.no / Duunitori, Job Market Finland |
| Czechia | Jobs.cz, Prace.cz |
| Turkey | Kariyer.net, Secretcv, Yenibiris, İŞKUR, LinkedIn |
| USA | LinkedIn, Indeed, Glassdoor, ZipRecruiter, USAJOBS (federal), Wellfound (startups), Dice (tech) |
| Canada | Job Bank, Indeed, LinkedIn |
| Australia / New Zealand | Seek, Indeed, Workforce Australia / Seek NZ, Trade Me Jobs |
| UAE / Gulf | Bayt, GulfTalent, Naukrigulf, LinkedIn |
| India | Naukri, Foundit, LinkedIn, Indeed |

Tell the person in one line why you suggest each ("biggest general site", "English-language jobs",
"public employment service"). For sites without email alerts, the hunt uses web search only.

## Work permit wording per region (facts to collect, no advice)

- **EU/EEA/Swiss citizens** can generally work across the EU/EEA; ask anyway, there are exceptions.
- **Everyone else:** which country, which permit, tied to an employer or not, expiry, would a new
  employer need to sponsor. US forms ask "authorized to work in the US" and "will you now or in the
  future require sponsorship"; UK forms ask about "right to work" and "sponsorship"; Gulf forms ask about
  visa status and transferability. Record the person's own answers; point to the official immigration
  website of that country if they're unsure.
- **Needs sponsorship to work abroad?** Suggest the official sources that list employers or jobs open to
  foreign hires, as extra search sources (web-search to confirm the current page): Germany: "Make it in
  Germany" (the government's portal for skilled workers, with a job listing); UK: the gov.uk "Register of
  licensed sponsors: workers"; Netherlands: the IND "Public register of recognised sponsors"; Ireland: the
  "Critical Skills Occupations List"; Canada: Job Bank. Ads saying "no visa sponsorship" are a hard filter
  for this person (B2). Never promise a visa; explain that the employer decides.
- **Sponsored permits often have a government salary floor** (e.g. Netherlands highly skilled migrants, UK
  Skilled Worker, Germany's EU Blue Card): point to the official page before the minimum (#6) is set; don't
  interpret it.
- **Regulated job or protected title abroad:** check the official finder (the ENIC-NARIC network,
  enic-naric.net, lists each country's centre; Germany: "Anerkennung in Deutschland" and its Recognition
  Finder) and tell the person only what it says; a work visa may separately need the degree checked as
  comparable. Web-search to confirm the current page. More for people searching abroad: `segments.md`.
