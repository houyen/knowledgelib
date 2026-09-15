# Project Agent Guidelines: knowledgelib_data

## Git Security & Committing Protocol
- **Zero Secrets**: Do NOT stage or commit any `.env*`, keys, certificates, bot tokens, or credentials.
- **Explicit Staging**: Never use `git add .` or `git add -A`. Always stage specific target files explicitly (e.g. `git add path/to/file.md`).
- **Pre-commit Check**: Always review `git status --short` and `git diff --cached --stat` before committing.
- **Identity Scope**: Ensure local git config has `user.name=houyen` and `user.email=tieutuyetnhi@gmail.com`.
