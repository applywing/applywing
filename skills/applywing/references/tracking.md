# Tracking and measuring (H)

**Open when:** the person says "I applied", "rejected", "I got an interview", "how was this week", "no
reply from X"; when a rejection arrives or was logged by the watch; and when de-duplicating during a job hunt.

## Where the tracker lives

- **Claude Code (main):** `tracker.xlsx` in the job folder, always changed through
  `python "<skill>/scripts/tracker.py" --file tracker.xlsx …` (created from the template on the first
  `add`; the person can open it in Excel, but it must be closed while the script writes):
  - `add --company … --position … [--city --channel --link --fit --decision --cv --status --note]`: a
    row with the same link or the same company + position is updated, never duplicated
  - `update --no N [--status …] [--note …] [--followup]` · `find --link …` / `find --company … --position …`
  - `list [--status …]` · `summary --days 7` · `due --days 10` (follow-ups due)
  Write the status words in the person's language consistently, or keep the English ones; `due` knows
  "Sent" in the common languages. `--note` goes into "Last update" with the date: keep it short. `due`
  computes the 10 days itself; the Follow-up column is the date a follow-up draft was suggested.
- **claude.ai:** see `claude-ai-mode.md` (Google Sheets or a table inside the profile file).

## Columns (H1)

| Column | Value |
|---|---|
| No | 1, 2, 3… |
| Date | application (or looked-at) date |
| Company | |
| Position | title in the ad |
| City / Remote | |
| Channel | LinkedIn · Indeed · <local site> · company site · agency · email · referral |
| Link | the job's page on the site |
| Fit | Strong fit · Good fit · Stretch · No fit |
| Decision | Apply · Skip · Maybe · Seen |
| CV file | path in the job folder (`CV/<company>-<role>/…pdf`) |
| Status | Prepared · Sent · Viewed · Interview · Test · Rejected · Offer · Closed |
| Last update | date + short note ("rejection email", "call on 5 Nov") |
| Follow-up | date a follow-up draft was suggested |
| Notes | |

## What to write when

- "Apply" and the CV is ready → status **Prepared**.
- "I sent it" → **Sent**, today's date ("yesterday" / another day: `--date YYYY-MM-DD`). The follow-up date (10 days later) goes into "Status" → pending
  follow-ups; mention it at the next "continue".
- "Your application was viewed" notification → **Viewed**.
- Rejection → **Rejected**; interview invite → **Interview** (`interview.md`); test/form/document request →
  **Test** + deadline in Notes.
- Ad closed or the person gave up → **Closed**.
- Evaluated but not applied → Decision **Skip** (reason in Notes); it won't come back in hunts.
- Same company + same role already there → update that row, no new row.

## Telling the person about a rejection

A rejection is news like any other in your status report: one factual bullet, then the rest of the report.
No comforting, no "annoying", no pep talk, no clichés ("everything happens for a reason", "at least…", "their
loss", "most applications end this way").

- **One bullet per rejection:** **<Company>, <role> (<city>), <time>:** what the email says in a few words
  ("they're going ahead with other candidates", "the position no longer exists"), and when the person applied
  if it helps ("you applied on 3 Oct"). Then: "Logged in the tracker."
- **Running total** from the tracker, once per report: "That's <n> rejections out of <m> applications; <k>
  interviews so far."
- **Reason:** only if the email gives one, or the facts clearly point to one, marked "probably" (e.g. rejected
  within an hour of applying → stopped at the first automatic screening, probably on the "<requirement>" the
  ad asked for). Otherwise no reason. Patterns across many rejections belong in the weekly review.
- **Not a rejection:** "the employer has finished collecting applications", "application received", "your CV
  was viewed": say "This is not a rejection" and log it as it is.
- Several rejections (e.g. the watch's "Not told yet" list) → a heading "Two rejections:" with one bullet each,
  and the total once.
- After an interview, the same format; then offer to note the questions they were asked for the next interview
  (`Interviews/<company>/basic-set.md`).
- Then go on with the report: other mail, new jobs, what the person needs to do (this week's plan).

Example (translate it):
```
**Mail:** two rejections:
- **Bluewave Travel Services, Customer Support Specialist (Warsaw), 15:20:** they're going ahead with other candidates. You applied on 3 Oct.
- **Vistula Parts Distribution, Junior Purchasing Assistant:** the position no longer exists.
Both logged in the tracker. That's 7 rejections out of 31 applications; no interview yet.
- **pracuj.pl, Example Retail Group:** the employer has finished collecting applications. This is not a rejection.
```

**When the person is fed up** ("again?!", "I'm sick of this"): no consoling and no questions about feelings.
Answer with facts (what is still open, what is coming) and what we can do next; if they want a break, fine.
Don't repeat the numbers from your previous message.

## Weekly summary (H2)

"How was this week" always runs the full weekly review in `review-and-learning.md` (it uses this summary
format plus `analyze`). Offer it when the review day has passed or the last summary date in Status is
older than 7 days; update the date afterwards. Rows missing channel / role family / route: ask for them in
one batch during the review. Format, in the person's language:

```
This week (dd.mm–dd.mm): <n> applications · <n> viewed · <n> replies · <n> interviews · <n> rejections
Total: <n> applications → <n> replies → <n> interviews
Channels: LinkedIn <n> (replies <n>) · <site> <n> (<n>) · …
Suggestion: <1–2 sentences>
```

- A channel with no signal for 2 weeks (and at least 5 applications) → suggest spending less time there.
- Repeated fast rejections from big-company systems for someone needing sponsorship → remind of B14
  (recruiter directly, agencies, smaller companies).
- Don't over-interpret little data ("still early").

## Follow-up email (H3)

For applications **Sent** with no reply after **10 days**, write a short follow-up (shown first, sent only
on the person's yes, G1), in the application's language: 3–4 sentences: which role, when applied, a brief
interest sentence, an easy question. Check it with `python "<skill>/scripts/check.py" --profile cv-data.json --text followup.txt`.
Write the date in Follow-up. At most one follow-up per application.

## "Check my email" and the daily watch

When the person says "check my email": read recent job emails in the job Gmail (only job-related:
invitations, rejections, tests, "application received"), update the tracker, and tell the person only what
they need to do. To do this every day automatically, see `watch.md`.
