# Job Search Profile: <Name>

<!-- Template for the assistant. Write the whole profile in the PERSON'S language (headings too);
     CV facts live in cv-data.json (CV language). Example in Turkish: examples/profile-document.md -->

> This document is the **single source of truth** for your facts. CVs, cover letters and form answers
> come only from here. If something changes (new job, city, salary, permit), tell me in the chat and I'll
> update it. The CV lines themselves are in cv-data.json; ask me to change them.
>
> Last confirmed: DD.MM.YYYY · Skill version: applywing v0.6

## 1. Identity and contact (CV header)
- Name on the CV:
- City, country:
- Phone:
- Job email:
- LinkedIn:

## 2. Target
- Countries / cities, remote, relocation:
- Job sites chosen (and why):
- Role families (2–3):
- Shifts, nights, weekends:
- Contract types:
- Earliest start / notice period:
- Situation (references/segments.md): working now / not working since MM/YYYY · first job / changing field /
  same field / senior manager-executive · abroad · gap · long career (e.g. "abroad · long career · #9
  skipped": "#9 skipped" marks only question 9)

## 3. Hard filters ("never show me")
- (e.g. ads requiring language X · night shifts · office-only in city Y)

## 4. Salary
| Role family | Figure to name | Minimum | Period, gross/net, currency |
|---|---|---|---|
| | | | |

## 5. Languages (honest level)
| Language | Level (A1–C2 / native) | On forms |
|---|---|---|
| | | |

## 6. Right to work (your own statement; not legal advice)
- Citizenship(s):
- Per target country: citizen / EU-EEA / permit type / tied to an employer? / expiry:
- In your own words (one sentence):
- Sentence for explanation boxes (CV language):

| Form question | Answer |
|---|---|
| Do you require visa / work permit sponsorship? | |
| Are you authorised to work without sponsorship? | |
| Do you have a valid residence permit? | |
| Are you an EU/EEA citizen? | |

## 7. Experience (per job)
### <Title> · <Company> · <City> · <MM/YYYY – MM/YYYY>
- A typical day (your words):
- Numbers you are sure of:
- **Things you did not do but people might assume:**
- Approved CV lines: in cv-data.json (key: `...`)

## 8. Software (what you can use on your own)
- Programs:
- Concretely in Excel:

## 9. Education, certificates, driving licence
-

## 10. Gaps and the real explanation
-

## 11. Never write
-

## 12. Sensitive topics (not to improvise in interviews)
- Topic → the sentence we prepared:

## 13. Optional questions
- Diversity questions: Prefer not to say (unless you say otherwise)
- Driving licence:

## 14. Target roles and bridges
| Target role | Bridge (from which real experience) |
|---|---|
| | |

## 15. Standard form answers (CV-language version in cv-data.json → `standardAnswers`)
- Currently employed / notice period:
- Earliest start (dropdown / date):
- Office, hybrid, remote, relocation:
- Start times, shifts, weekends:
- "Keep my data for future recruitment" box:

## 16. Alerts and channels
- Job email on the phone's Gmail app, notifications on: ☐
- Alerts: <site> ☐ · <site> ☐ · <site> ☐ (date)
- Search list:

## 17. Work rhythm (references/working-rhythm.md)
- Job hunt: every … · Quiet hours: … · Notify: only when I must act / daily summary
- Weekly review: <day, time> · Applications per week: … · Follow-ups / contacts per week: …
- Batch size: … · Thank-you emails: … · Side income: yes/no
- Language re-check: <language> on DD.MM.YYYY
- If-then lines in the weekly plan: yes / no (date)

## 18. Decisions (newest first; they override older notes)
- DD.MM.YYYY: …

## 19. Corrections (facts that changed, and where the old version went out)
- DD.MM.YYYY: …

## 20. Status (updated after every piece of work)
- Setup: Part 1 ☐ · Part 2 ☐ · Part 3 ☐
- Job folder: <path>
- Last job hunt: DD.MM.YYYY · Last email check: DD.MM.YYYY · Last weekly summary: DD.MM.YYYY
- Watch: <cadence>, since DD.MM.YYYY (or: off) · Pending interviews: …
- Pending follow-ups: (company · role · follow-up date)
- Not told yet (rejections the watch logged): company · role · date
- This week's plan (from Monday DD.MM.YYYY): what · day · where · how many, ✓ when done; "if … then …" lines
  (optional)
- Tips shown ("I can also…", at most one a week): what · date (or: no tips, date)
- Next step:

## 21. Applications: in tracker.xlsx (claude.ai mode only: this table)
| No | Date | Company | Position | City / Remote | Channel | Link | Fit | Decision | CV file | Status | Last update | Follow-up | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 22. CV DATA (claude.ai mode only; in Claude Code it is cv-data.json)
Structure: `assets/profile-template.json`. One block per CV language. Lines are approved; per job they are
only selected and ordered.

```json
{ }
```
