# Examples (entirely FICTIONAL)

The person (Ece Yildirim), companies, ads, phone and email are **made up**. No real personal data.
For testing, demos and showing the assistant the expected output format. Ece speaks Turkish, so the
conversation-side examples (profile document, evaluation) are in Turkish: that is what "in the person's
language" looks like.

| File | What |
|---|---|
| `profile-document.md` | Ece's filled profile file, in her language (Turkish), with Status and Applications |
| `profile-en.json` | Her CV DATA for English CVs (`standardAnswers` included), target Poland |
| `profile-tr.json` | Her CV DATA for Turkish CVs (jobs in Turkey, photo customary) |
| `sample-photo.png` | Placeholder silhouette (not a real person) for the photo option |
| `job-1-bluewave.md`, `job-2-vistula.md` | Two fictional ads |
| `job-1-selection.json`, `job-2-selection.json` | Per-ad selection (headline, profile, line keys, cover letter) |
| `linkedin-alert-email.txt` | Sample LinkedIn job alert email (source A) |
| `tracker-example.csv` | One-row tracker (for de-duplication) |
| `evaluation-example.md` | Job hunt result from the alert email + evaluation of two ads (in Turkish) |
| `output/` | CVs (PDF + Word) and cover letters produced by the script |
| `bad-examples/` | Deliberately bad selection, invented cover letter, honest answer (`--answer`) and the check results (`check-report.txt`) |

Re-create (from the skill folder):

```bash
cd examples
python ../scripts/build_cv.py --profile profile-en.json --out output/default-en
python ../scripts/build_cv.py --profile profile-en.json --job job-1-selection.json --out output/job-1-bluewave
python ../scripts/build_cv.py --profile profile-en.json --job job-2-selection.json --out output/job-2-vistula
python ../scripts/build_cv.py --profile profile-tr.json --photo sample-photo.png --out output/turkish-with-photo
python ../scripts/check.py --profile profile-en.json --job bad-examples/bad-selection.json
```
