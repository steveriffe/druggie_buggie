# Antigravity Agent Guidelines for Druggie_buggie

## Command Execution & Approval Best Practices
To ensure seamless execution without triggering repetitive manual approval prompts:

1. **Never Chain Shell Commands**:
   - Avoid `&&`, `;`, `||`, pipes `|`, or backtick command substitutions in `run_command`.
   - Chained commands disable the IDE's prefix-matching engine and force a unique, non-reusable confirmation prompt for the entire combined string.

2. **Prefer Static Script Invocations**:
   - Instead of complex inline bash or one-liner scripts (`python3 -c "..."` or `curl ... | jq ...`), write the logic into a file in `scripts/` or `src/` and invoke it directly:
     - `python3 scripts/harvest_all.py`
     - `python3 scripts/stage_bigquery.py`
     - `git push origin main`

3. **Subagent Execution Discipline**:
   - Subagents must not issue ad-hoc network exploration commands.
   - All network requests should be executed via Python standard library (`urllib.request`) inside consolidated scripts.
