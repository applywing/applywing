# Honesty rules: facts, CV and cover letter (A, C, D)

**Open when:** writing the profile, before every CV and cover letter, when the person says "add this too".

How rules are enforced: **[Rule]** you follow it · **[Check]** `<skill>/scripts/check.py` scans
automatically; on HATA (error) nothing is given out · **[Confirm]** the person must say "yes, correct".

The goal is not to force-fit the person to the ad. It is to present their real experience as strongly,
clearly and professionally as possible for recruiters and application systems. Nothing is invented; but
there is also no self-sabotaging "honesty" that volunteers weaknesses.

The check program works in every language for numbers, software names and the person's never/not-done
lists; banned phrases are covered in English, Turkish, German, Polish, Spanish, French, Italian and Dutch.
In other languages apply the phrase rules yourself.

## A. Facts: never bend

**The person's word is the source.** These rules stop *you* from adding things the person never said; they
are not there to police the person. If the person says "I know SAP" or "I'm fluent in English", take their
word: add it to `cv-data.json` in their words (ask at most one practical detail a CV line needs, e.g. which
module or how long; they can skip it). Never doubt, ask for proof or talk them out of it. If it contradicts
something they said earlier (e.g. SAP was in "did not do"), the newest statement wins: update the lists and
note it in `profile.md` → Corrections. Once it is in `cv-data.json`, the check lets it through.

| # | Rule | Enforced |
|---|---|---|
| A1 | CV, cover letter and form answers come **only from the person's confirmed profile**. Nothing that isn't there. | Rule + Confirm + Check (numbers not in the profile, written-out numbers too) |
| A2 | Title, dates, company names and numbers **do not change** per job. Only which lines are chosen and their order change. Translating a title into the CV language is allowed; upgrading it is not. | Check (selection by key only; title change = error) |
| A3 | Never write software they haven't used (SAP, ERP, CRM, Salesforce…). | Check (software not in profile = error) |
| A4 | One experience is not dressed up as another: paying suppliers ≠ collecting from customers; small-company admin ≠ shared service centre; customer service ≠ sales quota. | Rule |
| A5 | Years are not inflated; separate jobs are not merged into one expertise ("2 + 1 years" ≠ "3 years of X"). | Check (year claims flagged) |
| A6 | No unproven levels ("advanced Excel", "fluent"). Write what they can actually do. | Check |
| A7 | Gaps are not hidden with invented dates. Real activities (course, personal project, family) may be listed with dates. | Rule |
| A8 | CV, LinkedIn, forms and cover letter must not contradict each other. | Rule |
| A9 | Transferable skills are fine, but each must trace back to a real experience. | Rule |
| A10 | The person's **never-write** and **did-not-do** lists are scanned in every output (close variants too). | Check |
| A11 | Facts change: if the profile is older than 14 days, ask "anything changed?". | Rule |

## C. Writing the CV

| # | Rule | Enforced |
|---|---|---|
| C1 | **First 6 seconds:** headline fits the ad. A language advantage goes into the headline only if it helps for this ad; otherwise it stays in Languages. | Rule |
| C2 | The profile paragraph never starts with "Looking for…" (in any language). It states what they bring with 2–3 real proofs. | Check |
| C3 | No "I want to learn" framing. | Check |
| C4 | No volunteered gaps ("haven't used…"). If SAP isn't on the CV, it's clear they haven't used it. | Check |
| C5 | No empty adjectives: passionate, results-driven, highly motivated, team player… (and equivalents). | Check |
| C6 | Concrete names, numbers and tasks. | Rule |
| C7 | Priority: experience closest to the ad → numbers → transferable skills → language/location → the rest. | Rule |
| C8 | Unrelated or older experience stays short ("Other Experience", one line, max 1 bullet; the heading can be renamed with `headings`, e.g. "Earlier Career"). | Check |
| C9 | No AI smell: no em dashes or arrows, no copying the ad, no identical sentence pattern in every CV. | Check (dashes) + Rule |
| C10 | Using AI is not presented as a skill ("with AI assistance"). | Check |
| C11 | **Application systems (ATS):** standard section headings in the CV language; no letter-spacing or all-caps tricks; page limit of the country; one employer per line; PDF text readable. For English/international CVs, write the name in plain Latin letters (Ş→S, ł→l). | Check (the script enforces and verifies) |
| C12 | **Country customs** from `countries.md`: pages, photo, personal details, consent line. | Script + Rule |
| C14 | **Parsing details learned in practice:** separate contact items with " \| "; one line per other job; projects apart from jobs; file names by role family, never the company (`family` in the job file); the same name spelling everywhere (some systems split names with special letters). | Rule + Script (file names) |
| C13 | The real title stays. If "overqualified" is a worry, the profile paragraph leads with the work done, not the title. | Rule + Check (headline copying the ad's title they never held = error) |

**Profile paragraph pattern (don't reuse the same sentence in every CV):** [closest real work + scale] →
[second proof] → [language / location / availability if it helps]. 2–4 sentences, under 650 characters.
Someone changing field may end with the direction of the move, phrased as what they bring ("…; now moving into
IT support."), never as wanting to learn (C3).

## D. Cover letters and messages

| # | Rule | Enforced |
|---|---|---|
| D1 | Short (100–200 words; shorter is better; follow the country: an Anschreiben may be a bit longer): which role → strongest 1–2 real experiences → language, location or availability if relevant. | Check (length warning) + Rule |
| D2 | No CV summary, no list of gaps, no ending with "I would like to learn…", no empty praise ("prestigious", "amazing opportunity"). | Check + Rule |
| D3 | "Why this company?" uses only what the ad says; never invent facts about the company. | Rule |

## Writing the profile (setup)

- Each job's lines in the CV language, past tense, one sentence, concrete: what + how much/with whom + result.
- Only numbers the person is sure of. If approximate, write "around".
- Give each line a short key (`orders`, `refunds`); job selections use these keys.
- Write 4–6 lines per job with different emphasis; each application picks 2–4. Show all lines of a job in
  one message, each with a short explanation in the person's language; they flag wrong or exaggerated ones.
- "Did not do but people might assume" → `notDone`; "never write" → `neverWrite`, in the CV language
  (e.g. "SAP", "managing a team"). The check looks for them and close variants in every output.
- Software they use → `itSkills`. Software not listed there (e.g. Salesforce) in any output = error.
- Every fact that may appear in a cover letter or form (salary, start date, permit sentence) goes into
  `standardAnswers`, otherwise the number check stops it.
- To switch off a rule knowingly (e.g. they truly hold an advanced Excel certificate), add the rule id
  to `lintAllow` (`excel-seviye`) and tell the person why.

## Quality check before every CV and cover letter

- [ ] Did I invent anything? Is every number, program and level in the profile?
- [ ] Are structural blockers classified correctly? (`job-evaluation.md`)
- [ ] Is the headline really for this ad? Language advantage only if it helps?
- [ ] "Looking for…" or "I want to learn…" anywhere?
- [ ] Did I volunteer weaknesses?
- [ ] Did I exaggerate (years, field, title)?
- [ ] Do CV, LinkedIn, form and letter agree?
- [ ] Does the letter tell the recruiter what the person brings?
- [ ] Country customs followed (pages, photo, consent line)?
- [ ] Does it read like a person wrote it (not the same pattern every time)?
- [ ] Did `check.py` / `build_cv.py` pass?

## Bad / good examples

| Bad | Why | Good |
|---|---|---|
| "Looking for a junior role where I can learn the process." | C2, C3 | "Bringing hands-on order tracking and supplier invoice checks into a structured purchasing team." |
| "I haven't used SAP yet, but I'm a fast learner." | C4, C5 | (No SAP at all; if asked in an interview, the honest answer from `interview.md`) |
| "Advanced Excel user." | A6 | "Excel: filters, VLOOKUP and basic PivotTables for order tracking." |
| "5 years of customer service" (3 + 2 years in different jobs) | A5 | "Three years of customer support, then two years of order administration." |
| "Tutkulu, sonuç odaklı bir takım oyuncusuyum." | C5 | Concrete work and numbers, in Turkish |
