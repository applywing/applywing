# Review and learning: why rejections happen, where to focus

**Open when:** the weekly review is due (day from `working-rhythm.md`), the person asks "how is it going /
why no replies / what should I change", after about 10, 20 and 50 applications (second-eye review), and
when the person corrects a fact.

## Weekly review (15 minutes, written in the person's language)

1. Run `tracker.py summary --days 7` (this week, the week before, replies that arrived this week),
   `tracker.py analyze` and `tracker.py due`.
2. Write `reviews/week-<review date YYYY-MM-DD>.md` in the job folder. Show it in **three short messages**:
   (1) the numbers and last week's plan, (2) the proposed plan with "OK?", (3) only after a yes, the optional
   "if … then …" offer.
   - this week vs last week (applications, replies, interviews), replies that arrived this week
   - **pace check:** applications vs the plan the person agreed (or the Work rhythm target; no target → don't
     judge pace). Two weeks below → say it once and ask: keep the number or set a smaller one?
   - **channels / role families / application routes:** a signal (interview, test, recruiter contact;
     rejections are not a signal) → do more there; 2 silent weeks with at least 5 applications → do less there
   - follow-ups due
   - last week's plan vs what was done, from the ✓ marks and the tracker: done / not done / moved. Don't ask
     why; if the person gives a reason, note it.
   - **next week's plan** (below)
   - "fixed decisions" (from `profile.md` → Decisions) unchanged, or what changed and why
3. Update Status → "Last weekly summary" and "This week's plan".

The watch's scheduled weekly review (`watch.md`) only runs the numbers and saves the file; the plan is agreed
with the person at the next "continue".

## Next week's plan

Background for you (don't quote it to the person as a promise): in a randomised trial with about 1,100
young job seekers in South Africa (Abel, Burger, Carranza & Piraino 2019), those who wrote down what, when and
how they would search got about 30% more job offers; reminders on top of the plan added nothing. So agree on a
concrete plan with the person instead of nudging them during the week.

- **3–5 lines, each: what · which day · where · how many.** Example: "Tuesday morning: 2 applications from
  POOL.md (pracuj.pl, Customer Support)". At least one line uses a channel tried less so far (a recruiter
  message, a referral, an agency). The application lines add up to the weekly target, or the target is
  lowered together with the person. A smaller plan is fine; an unrealistic one is not.
- **1–2 "if … then …" lines (optional).** Offer once, in one sentence with ready examples the person can take
  as they are ("Fine to skip."): "If Tuesday gets busy, then Wednesday morning instead." "If a rejection
  comes, then that evening I still send the one recruiter message." "If two weeks pass with no replies, then
  we move 2 applications to agencies." If they say no, write "if-then: no (date)" in `profile.md` → Work
  rhythm and don't offer again unless they ask.
- When the snag in a line happens, remind them of their own line, once.
- Save it in the review file and in `profile.md` → Status → "This week's plan (from <Monday>)"; the new plan
  replaces the old one, if-then lines included. Mark items ✓ when done. At every "continue" the first unmarked
  item (overdue first) is the default suggestion; once the plan's week is over, suggest the weekly review.
- End the review with one "By the way, I can also …" line if no tip was shown this week (`SKILL.md` §4 →
  "Showing what else I can do").

## Reading rejections (in the weekly review, when `analyze` flags a pattern; never right after a single rejection; as likely explanations, never as certainty)

- **Speed tells you who read it:** within about a day → automatic screening; 3–7 days → screening questions
  plus a quick human look; opened and rejected within the hour → a human read it.
- **Fast rejections clustering on one application route** (often big-company systems with structured
  work-permit or "do you have X experience" questions): the knock-out questions probably decide. Keep answers true
  (E2), and move effort to routes where a human reads first: the company's own form, the recruiter directly,
  agencies, referrals.
- **"Viewed" but silent, many times:** the first 6 seconds of the CV (headline, profile) don't match the
  ad. Tighten the headline and the first lines (C1, C7).
- **Easy-apply style one-click applications all silent:** lower their priority.
- **Regulated fields + an honest "No" to "experience in X?"** → near-automatic rejection. Prefer roles where
  the bridge is strong; don't stop being honest.
- **Most common reason to drop ads early** is usually the local language, not the permit: if the person is
  learning it, plan the re-check (working-rhythm #9).
- **Niche advantage pays:** roles that need the person's rarer language or combination are fewer but answer
  more. Keep them at the top.

Treat these as hypotheses; the person's own `analyze` numbers decide (with fewer than ~15 applications say
"too early to tell").

## Second-eye review (after about 10, 20 and 50 applications)

1. Build `reviews/second-eye-<n>.md`, self-contained: the rules used, every application (role, CV and
   letter actually sent, form answers), what you suspect went wrong, and numbered questions. Ask for harsh
   criticism.
2. Have it reviewed by a fresh reviewer: a subagent or a new session with the instruction "You don't have to
   agree. Invent nothing. Mark what you're unsure about." (The person may also show it to a friend.)
3. Turn the feedback into dated decisions in `profile.md` → Decisions; newer decisions override older
   notes. The next review starts with a table "feedback → change → status (done / partly / postponed)" and a
   before/after of the CV.

## When the person corrects a fact

1. Fix `cv-data.json` / `profile.md` and log it in `profile.md` → Corrections with the date.
2. List every past use of the old claim (CVs in `CV/`, letters, form answers, messages) and tell the person
   where it went out. Fix the files before any reuse.
3. Don't re-argue choices the person made about their own story; flag a factual risk once at most.

## Proof the person can build (suggest when gaps repeat in the analysis)

Recent, checkable items: a free or cheap language test score, a free vendor course for the system ads keep
asking for, a short certificate, an anonymised work sample, short written references. A CV line appears only
once the item is real (e.g. "Training: <course>, in progress since MM/YYYY"), approved like any other line.
