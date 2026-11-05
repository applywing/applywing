# Form answers (E)

**Open when:** the person is filling an application form, a form question is unclear, or standard
answers are written during setup.

**You fill the form with these answers and send it on the person's yes** (`applying.md`). If the person
fills it themselves, give them the list at the end of this file.

## Rules

| # | Rule |
|---|---|
| E1 | **Same answers on every form** (the profile's standard answers). If an answer changes, update the profile first. |
| E2 | **Never answer the work-permit question falsely.** If they really need sponsorship or a new permit, "no sponsorship needed" is never ticked: it surfaces at hiring and kills the offer. In a free-text box: one calm sentence, no unnecessary detail. |
| E3 | Salary: the figure to name + the minimum. If the ad shows a range, suggest the middle (if not below the minimum) and let the person choose; this is the one exception to E1. Match gross/net, period and currency to the form. The **minimum stays only in profile.md**: never in cv-data.json, a form or a letter. |
| E4 | Honest language level, even if the ad asks for more. If the form uses another scale ("Intermediate / Upper-intermediate"), use the mapping in the profile. |
| E5 | ID numbers, date of birth, passport: **never asked for or stored by the skill**; the person types them. |
| E6 | Consent boxes (GDPR, terms, "I declare…"): read them, summarise each in one line before sending, tick on the person's yes. Never tick a declaration that isn't true. |
| E7 | Optional diversity questions: "Prefer not to say" unless the person says otherwise. |
| E8 | **A question you have no answer for.** **Close variant** of something the person already told you (same fact, other wording or format) → fill it from that answer and mark it in the summary. **New fact** → leave the field empty and ask the person before sending; never guess. Details below. |

## E8 in practice: close variant or new fact?

**Close variant: take the small risk, fill it, say where it came from.** The answer follows directly from
something already in the profile:
- "Notice period" when the profile says "currently employed: no" → "None / immediately".
- "Are you legally allowed to work in <country>?" when the permit answers are recorded.
- The language level asked as "fluent / conversational / basic", or a different scale, mapped from the
  recorded A1–C2 level (E4).
- A salary dropdown with ranges → the range that contains the recorded figure.
- "Willing to work hybrid?" when the profile says office, hybrid or remote are all fine.
- "Where did you hear about this job?" → the channel the ad came from.

In the summary before sending, mark each one: `"Notice period": None (from your answer "not employed now")`.
The person sees it and can correct it with one word.

**New fact: don't fill, don't send, ask.** Nothing in the profile answers it:
- a tool, skill, certificate or licence not recorded;
- years of experience in something not recorded;
- willingness to travel or relocate, or a shift pattern, that the profile doesn't cover;
- a yes/no about the person's history: a past application to this company, references, a criminal record,
  health, previous salary;
- any declaration.

Leave the field empty and put the question in the summary under "Needs your answer". When the person
answers, fill it, add the answer to `standardAnswers` and `profile.md` so the same question is never asked
again, then ask "Send it?". In a batch, fill everything else and ask all the open questions in one message.

## Form nuances learned in practice

- **Experience questions:** a broad one ("experience in a similar role / customer-facing work") may get a
  defensible umbrella figure built from real jobs; a narrow one ("years of X") gets the true separate
  duration. Never add up different jobs into one specialty (A5).
- **Start date:** "immediately" only while it is true; if a new employer needs a permit first, give the
  realistic lead time ("within X weeks") once the person knows it.
- **Salary for a stretch role:** suggest the lower third of the ad's range (still not below the minimum);
  middle of the range for a reasonable fit.
- **One permit matrix:** the same permit answers on every form; inconsistent answers across forms caused
  rejections and confusion. If a form asks a yes/no that doesn't fit the person's situation, stop and ask.
- **After a site auto-fills from the CV:** read every field; fix garbled names, dates and titles, and delete
  skills the site suggests that the person doesn't have.

## Standard answers (filled together at setup)

The profile's "Standard form answers" section has this structure; the same answers in the CV language
live in `cv-data.json` → `standardAnswers` (the check program verifies form numbers against them; example:
`examples/profile-en.json`). If a question isn't covered, ask the person when the form shows it and add
the answer to both places.

**Identity and contact:** name as on the CV · job email · phone · city · LinkedIn · address (only if the
person wants it stored) · date of birth / ID / passport → **the person types them**.

**Status:** currently employed? · notice period · earliest start (dropdown and date field).

**Salary:**

| Role family | Figure to name | Minimum | If net is asked |
|---|---|---|---|
| … | … | … | … |

**Right to work (most sensitive; the person's own statement, not legal advice):**

| Form question | Answer |
|---|---|
| Free text / explanation box | (one sentence the person approved) |
| "Do you require visa / work permit sponsorship (now or in the future)?" | Yes / No |
| "Are you authorised to work in [country] without sponsorship?" | Yes / No |
| "Do you have a valid residence permit?" | Yes / No |
| "Are you an EU/EEA citizen?" | Yes / No |
| Yes/No only, "Are you currently authorised to work?" | (clarify with the person) |
| Mandatory "I have the right to work" declaration box | **Not ticked** if untrue; ask the person; maybe write to the recruiter |

Grey zones to flag (not to decide): a permit that expires during the likely employment ("now **or in the
future**" questions), a permit that is not tied to an employer but has conditions. Say what the form asks,
what the person's facts are, and let them decide. If unsure about their own situation: "Best to confirm on
the official immigration website of that country or with the recruiter." No interpretation [G6]. Don't volunteer details like who pays permit fees;
answer truthfully if asked.

**Languages:** CV level per language + mapping to common form scales.

**Software / Excel:** the CV sentence · "Advanced / good Excel?": not without proof; pick the middle level.

**Work mode:** office/hybrid where · fully remote · relocation · start times, shifts, nights, weekends ·
driving licence.

**Education:** school, field, year (same as the CV).

**Consent boxes:** summarised for the person, ticked on their yes (E6). "Keep my data for future recruitment" box: their preference is in
the profile (`futureRecruitment` in cv-data.json; the Polish CV consent line includes future recruitment only
when it is true).

**"Why this role / company?" free text:** specific to each ad, 2–3 sentences, **no invented facts about
the company**; only what the ad says and the person's real experience [D3]. Check it:
`python "<skill>/scripts/check.py" --profile cv-data.json --text answer.txt --job "jobs/<file>.json"`
(For an honest answer to a direct screening question like "Do you have X experience?", add `--answer`.)

## When the person fills the form themselves

When the person says "I'm filling the form" (or there is no browser), give a short copy-paste list for that ad, in the form's
language:

```
Company: … · Role: …
- Earliest start: …
- Salary expectation: … (range in the ad: … → middle …)
- Right to work (explanation): "…"
- Sponsorship required?: …
- Languages: …
- Why this role (2–3 sentences): …
You type yourself: date of birth, ID numbers, consent boxes. Read everything before you submit.
```

When they say "submitted", log it in the tracker (`tracking.md`).
