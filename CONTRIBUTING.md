# Contributing to VerifAI

## Workflow

```text
Issue → Branch → Commits → Pull Request → CI green → Squash-merge → Issue closed → Card moves to Done
```

1. **Pick an issue** from the [Sprint 2 board](https://github.com/users/itzhimanshugt/projects/2). Every graded concept has one issue titled `[Cn] …`.
2. **Create a branch** from an up-to-date `main`:

   | Type | Pattern | Example |
   |---|---|---|
   | Feature / concept | `feat/c<n>-<short-name>` | `feat/c12-chunking` |
   | Docs | `docs/<short-name>` | `docs/prd-revision-v2` |
   | Chore / tooling | `chore/<short-name>` | `chore/c2-github-workflow` |
   | Fix | `fix/<short-name>` | `fix/empty-chunks` |

3. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/): `feat(ingestion): …`, `fix(rag): …`, `docs: …`, `chore: …`, `test: …`.
4. **Open a PR** into `main` using the template. It must name the concept, link the issue (`Closes #n`), show evidence, and include walkthrough notes for the concept video.
5. **Merge** with squash once CI passes and all review conversations are resolved. The branch is deleted automatically.

## Rules on `main`

`main` is protected. These rules apply to everyone, including admins:

- No direct pushes: every change goes through a pull request.
- Required checks: `lint-and-test` (ruff + pytest) and `secret-scan` (gitleaks).
- The branch must be up to date with `main` before merging.
- All review conversations must be resolved.
- Linear history (squash merges only); no force pushes; the branch cannot be deleted.

## Local checks before pushing

```bash
ruff format .
ruff check .
pytest
```

## Secrets

Keep keys only in `.env` (git-ignored). Never paste keys into code, issues, PRs or logs. `.env.example` lists the variable names.
