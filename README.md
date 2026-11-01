# Applywing v0.6.0

A **free** job application assistant for **Claude Code**, for anyone, applying in any country. It reads
your CV, searches the job sites you choose (and suggests
good ones for your country), filters out ads that would reject you anyway, writes an honest CV and cover
letter for each job following that country's customs (Word + PDF), tracks your applications, prepares you
for interviews and, if you want, checks every morning and only pings you when you need to act.
**It fills in the application forms too, and nothing is sent without your OK; nothing goes on your CV that you didn't tell it.** Your files stay in a
folder on your own computer; job sites get only what you approve for each application.

Claude plans have a usage limit. To save it, the assistant searches job sites and emails with a lighter
Claude model and keeps the stronger one for your CV and letters.

## Install (one sentence)

Open Claude Code (the Claude desktop app's **Code** tab, or `claude` in a terminal) and paste:

```
Install this: https://github.com/applywing/applywing
```

Claude reads [INSTALL.md](INSTALL.md), asks your permission twice, and it's done. Then open a new session
and write "I'm looking for a job" in your language.

Claude Code needs a paid Claude plan (Pro or Max). Using claude.ai chat instead? Download
`docs/indir/applywing.zip` → Customize → Skills → Upload a skill.

## What's in this repository
- `skills/applywing/`: the skill (instructions, rules, country guide, CV builder, honesty
  checker, tracker, fictional examples)
- `.claude-plugin/`: plugin and marketplace definition
- `INSTALL.md`: installation steps Claude follows
- `docs/`: download page (Turkish / English) and the ZIP

## Privacy and limits
Your data stays on your computer (and in your own Claude account). The assistant fills in forms and
sends applications or emails only after your yes for each one; it never asks for passwords, ID numbers or
card details. No job or
interview guarantee; check every output before sending.

A free skill that works with Claude. Not affiliated with Anthropic. License: MIT.

---

**Türkçe:** Claude Code için ücretsiz iş başvuru asistanı; hangi ülkede iş ararsan ara kullanabilirsin.
Kurulum: Claude Code'u aç, şunu yapıştır: `Bunu kur: https://github.com/applywing/applywing`.
Sonra yeni oturumda "iş arıyorum" yaz. Dosyaların kendi bilgisayarındaki bir klasörde durur; asistan formu
doldurur ama senin onayın olmadan hiçbir şey göndermez.
