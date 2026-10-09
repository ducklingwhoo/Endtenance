# Contributing

Thanks for helping! Endtenance is intentionally small: all the code is in one file,
`endstone_endtenance/__init__.py`.

## Found a bug or have an idea?
Open an issue and include your Endstone version, Python version and the console log.

## Making a change
1. Fork the repo and create a branch.
2. Edit `endstone_endtenance/__init__.py`.
3. Build it and test it on a local Endstone server (see "Build it yourself" in the README).
4. Add a line to `CHANGELOG.md` under an `## [Unreleased]` heading.
5. Open a pull request that explains what you changed and why.

## Style
- Keep it simple and readable; avoid extra dependencies.
- Never crash the server: wrap risky calls in `try/except` and log the problem.
- Keep config keys backwards compatible where possible.

By contributing, you agree your work is released under the project's Apache License 2.0.
