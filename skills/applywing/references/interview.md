# Interview preparation: "the sceptical interviewer" (F)

**Open when:** the person says "I got an interview", "I have a phone call", "they sent a test".

## Rules

| # | Rule |
|---|---|
| F1 | Read the CV sent to that company as a sceptical interviewer. For every fragile line, prepare the likely question and an **honest** answer. |
| F2 | Mark with 🔴 what the person must clarify beforehand (gaps, closed company, missing numbers, reason for leaving), so they never have to improvise. |
| F3 | Live tests are done **without AI**. If one is likely for a skill on the CV (e.g. an Excel test), offer a practice exercise; no doubting, the person decides. |
| F4 | Honest pattern for "do you know system X?": first "I haven't used it", then the transferable experience. |
| F5 | Put the CV, cover letter and form answers sent to that company in front of them (from the tracker and saved files). |

## Steps

1. Find the company in the tracker; set status to "Interview" with the date. Open the CV and letter from
   `CV/<company>-<role>/`. Re-read the ad.
2. If the person shares the invitation email, read it (don't click links). List: date, time, format
   (phone/video/onsite), with whom, documents or tests requested, deadlines.
3. Write a prep document with this structure (explanations in the person's language, answer drafts in
   the interview's language). Save it as `Interviews/<company>/prep.md` in the job folder. With a few days
   to go, add the boot camp below.

## Prep document structure

```
# <Company> · <Role> · <date, time, format>

## 🔴 Clarify before the interview
1. <topic>: <why they'll ask> → <what I need from you: one true sentence>

## The 3 questions every interview has
1. "Tell me about yourself." → 60-second draft (CV order, facts only)
2. "Why this role / why us?" → 2–3 sentences based only on the ad
3. "What are you doing now?" / "Why did you leave …?" → the person's confirmed facts

## Riskiest questions for this CV
- "<question>" → honest answer draft: "…"  (which CV line it comes from)

## Live test risk
- <skill>: the CV says "<sentence>". No AI in tests. Practice: <concrete exercise, e.g. build a pivot
  table and a lookup 3–4 times on your own>.
  If you can't: "I'm not fast at this under test conditions yet. Let me walk you through what I would build and why."

## If asked about the right to work
- The profile's approved sentence (same as on forms). Short and calm.

## 2–3 questions you can ask
- Real curiosity about the tasks in the ad (what success looks like in 3 months, team, training)

## Bring / have ready
- The same CV, cover letter, form answers, (documents if any)
```

## Interview boot camp (when there are a few days until the interview)

Make a folder `Interviews/<company>/` and, with the person, work through it:

| File | What |
|---|---|
| `PLAN.md` | Day-by-day plan until the interview: a "your tasks / my tasks" table with a status per task |
| `cv-native.md` | The CV that was sent, translated into the person's own language, so they know every line by heart |
| `basic-set.md` | A 70-second self-introduction + 6–8 short answers to memorise, in simple sentences of the interview language; the person rewrites them in their own words |
| `dialogue.md` | A predicted interview dialogue using only true facts, with the 🔴 items resolved |
| `crash-course.md` | Only if the field is new: 4–6 short modules on the role's basics + a quiz (no claims of experience) |
| `language-kit.md` | For non-native speakers: pronouncing work terms, saying numbers / dates / money, "sorry, could you repeat / rephrase", buying time, closing questions |
| `skill-test.md` | If a live test is likely (Excel, typing, a case): an exercise in the role's context, done **without AI** |
| `rehearsals.md` | Mock interviews: a prompt the person pastes into a voice-mode AI (e.g. the Claude app's voice mode): "You are the interviewer for <role> at <company>. Speak simple English. Use only these facts: … Ask one question at a time, follow up once, give a score out of 10 and the best and weakest answer at the end." After each rehearsal log: score, best part, weakest part, 3 golden rules for next time |

- **Research (ask first):** the ad, the company's public site, and if the person wants, the interviewers'
  public professional profiles. Optionally a short, honest message to someone in the same team; by email:
  shown, then sent on the person's yes; on LinkedIn the person sends it (no automation there).
- **Tech check the day before (video interviews):** test call with the same app, camera at eye level, light
  in front, headset, microphone recognised by the app, phone hotspot as backup, charger. (A real interview
  started with an unrecognised microphone.)
- **Reminders:** the day before (rehearsal + tech check) and one hour before. If the person wants quiet,
  pause the watch's job notifications; mail from that company always counts as action.
- Live tests can come 24–48 hours after an invite: if the CV claims a skill, practise it now (F3).

## Honest answer patterns

- **System not used:** "I haven't used <SAP> professionally yet. My experience includes <real work>, so the
  underlying workflow is familiar to me." (Only when asked; never in the CV or letter.)
- **Asked for a number they don't have:** "I don't have an exact figure; it was roughly <confirmed range> /
  I'd rather not guess." Never invent.
- **Gap:** the profile's true explanation, one sentence, not defensive.
- **Closed company / leaving:** the real reason, no blame, end with a forward-looking sentence.
- **"Aren't you overqualified?":** focus on the work done and why this role makes sense; don't shrink or
  inflate the title.

When checking these drafts with `check.py --text`, add `--answer`: admitting a gap is fine in an answer
to a direct question [F4, B11].

## After the interview

- Ask: "How did it go? What did they ask?" Add notes to the tracker and the prep document; questions that
  surprised them go into `basic-set.md` for the next interview.
- No news about 10 days after the interview → a short follow-up email (`applying.md`: show, send on yes).
- Thank-you email if wanted: written, checked with `check.py --text`, shown, sent on the person's yes.
- When the result comes, update the status (Offer / Rejected). A rejection: tell it the `tracking.md` way
  ("Telling the person about a rejection").
