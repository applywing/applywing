# Running on claude.ai (web / phone chat) instead of Claude Code

**Open when:** you cannot run shell commands or write files on the person's computer (claude.ai chat,
the Claude phone app, or the desktop app's chat tab). The main design is Claude Code with a local job
folder (`SKILL.md` §3); here the same work is done with a Claude Project and, if possible, Google Drive.

## Differences

| Topic | Claude Code (main) | claude.ai (this file) |
|---|---|---|
| Where files live | Job folder on the computer | Google Drive "Job Search" folder, or a Claude Project file |
| Remembering between chats | `CLAUDE.md` + `profile.md` in the job folder | Project instructions + profile file in the project |
| Scripts | Run locally with Python | Run in Claude's sandbox; needs "Code execution and file creation" on |
| Output files | `<job folder>/CV/<company>-<role>/` | Download folder of the sandbox (usually `/mnt/user-data/outputs`) |
| Skill path `<skill>` | The skill's base directory | Usually `/mnt/skills/user/applywing` |
| Watch mode | Possible (scheduled tasks) | Not available |

## Project (end of Part 1)
"Every chat starts from scratch; with a 'Job Search' project we can always continue where we left off."
Steps: left menu **Projects** → **New project** → name `Job Search` (in their language) → paste into
**Instructions**:
```
In every chat in this project, use the applywing skill. First read my profile (in Google Drive "Job Search Profile" or the job-search-profile.md file in this project), then continue from its "Status" section.
```
From then on they open new chats inside this project and type "continue" (in any language).

## Code execution and web search
- If scripts can't run: first give their answers so far as a profile file, then "Settings → Capabilities →
  Code execution and file creation → on". If packages can't install, an internet / package access option
  on the same page must be on.
- Before a job hunt: if web search is off, "turn on **Web search** in the tools (+) menu".

## Drive and Gmail connection (Part 3)
Why: "Then your profile and tracker save automatically, and I can read job alerts and replies." Steps
(desktop): **Settings → Connectors** → **Google Drive** → **Connect** → choose the **job account** → allow.
Same for **Gmail**. After connecting, test: can you create the "Job Search" folder and a profile document
in Drive? Can you search Gmail? Say what didn't work and use the Project route.

## Saving
- **Drive route** (connected and writable): "Job Search Profile" document in the "Job Search" folder (the
  readable profile + CV DATA JSON block at the end); tracker "Job Search Tracker" (Google Sheets, columns
  from `assets/tracker-template.csv`, translated).
- **Project route:** give `job-search-profile.md` (readable profile + CV DATA block + "Applications" table)
  as a download: "Download → Projects → Job Search → project files → + upload; delete the old version."
- Before running scripts, save the CV DATA block unchanged as `profile.json` in the sandbox; pass
  `--out /mnt/user-data/outputs/<company>` so the person can download the files.
