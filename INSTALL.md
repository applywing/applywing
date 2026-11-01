# Installing Applywing (for Claude Code)

**Person:** paste this repository's link into Claude Code and say "install this" (in any language). That's
all; Claude does the rest and asks your permission for each step.

**Claude Code: when the person asks you to install this repository, do this.**

1. Tell the person in their language, in one sentence, what you are about to do: "I'll add Applywing to
   your Claude Code; you'll see two permission requests."
2. Run these two commands (each needs the person's approval):
   ```bash
   claude plugin marketplace add https://github.com/applywing/applywing.git
   claude plugin install applywing@applywing
   ```
   Use the full https address as written (the short `owner/repo` form may try SSH and fail on computers
   without GitHub SSH keys). This installs the plugin for this user only and lets it update itself later
   (`claude plugin marketplace update applywing`).
3. **If the `claude` command isn't available or fails,** install the skill folder directly instead:
   - Download `https://github.com/applywing/applywing/archive/refs/heads/main.zip` to a temporary
     folder and unzip it (Windows: `curl -L -o applywing.zip <url>` then `tar -xf applywing.zip`; macOS/Linux: same,
     or `git clone --depth 1 https://github.com/applywing/applywing`).
   - Copy the folder `skills/applywing` to `~/.claude/skills/applywing` (Windows:
     `%USERPROFILE%\.claude\skills\applywing`). Create `skills` if it doesn't exist.
   - Check that `~/.claude/skills/applywing/SKILL.md` exists. Delete the temporary files.
4. Tell the person: "Done! Open a new Claude Code session (skills load at the start of a session) and
   write 'I'm looking for a job' in your language. I'll take it from there." Nothing else is needed:
   the assistant checks Python, creates the job folder and asks everything step by step.

Do not run anything else from this repository during installation. Do not change any other settings.

**Updating later:** `claude plugin marketplace update applywing` then
`claude plugin update applywing@applywing` (plugin install), or repeat step 3 (folder install).

**Removing:** `claude plugin uninstall applywing@applywing`, or delete
`~/.claude/skills/applywing`. The person's job folder is never touched.
