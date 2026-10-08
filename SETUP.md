# Setup (about 5 minutes)

1. **Repo name must equal your username**: `Mohid-Abbas/Mohid-Abbas`, public, default branch `main`.
   Push the contents of this folder to it.
2. **Actions → Workflow permissions**: Settings → Actions → General → *Read and write permissions*
   (only needed if the first run fails with a 403 on `git push`).
3. The push itself triggers the first run, which **replaces the demo data** in this zip with your
   real activity. You can also press *Actions → Update profile → Run workflow*.
4. **Private work missing from the graph?** The built-in token only sees public activity. Create a
   classic personal access token with just `read:user`, add it as a repo secret named `PROFILE_TOKEN`.
   Also tick *Profile → Contribution settings → Include private contributions*.
5. Edit `config/profile.toml` (text, stack, which repos count as hardware) or `README.template.md`
   (layout). Never edit `README.md`; it is overwritten.

Change which projects show: **pin/unpin repos on GitHub**. The next run picks it up.

Preview locally without touching GitHub: `python3 scripts/build.py --demo` (invented data) or
`python3 scripts/build.py --offline` (re-render from the last fetched `data/profile.json`).
Requires Python 3.11+. No packages to install.
