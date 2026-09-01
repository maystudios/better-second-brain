---
type: concept
name: Shared-Worktree Commit Integrity
aliases:
  - multi-agent Git ownership
  - pathspec sweep hazard
tags: [software/git, version-control, multi-agent, commits, code-review]
sources:
  - "[[wiki/sources/git-commit-pathspec]]"
  - "[[wiki/sources/git-add-patch]]"
  - "[[wiki/sources/git-diff-review]]"
  - "[[wiki/sources/maypaintworks-multi-agent-evidence]]"
created: 2026-09-01
updated: 2026-09-01
status: stable
---

# Shared-Worktree Commit Integrity

Shared-worktree commit integrity is the rule that a commit must contain only the intended hunks, not
merely the intended filenames. Git pathspecs select files; they do not encode which actor owns which
changes inside a selected file. ([[wiki/sources/git-commit-pathspec]])

## How it shows up

- `git commit -- <file>` records that tracked file's current working-tree contents. In a shared
  worktree, another agent's uncommitted hunks can enter the commit under the first agent's message.
  A real incident left clean `HEAD` uncompilable while the dirty worktree looked coherent.
  ([[wiki/sources/maypaintworks-multi-agent-evidence]])
- `git diff --cached --name-only` proves only the file set. Review scale with cached `--stat`, then
  content with the cached patch; require the stat to agree with the message.
  ([[wiki/sources/git-diff-review]])
- When two actors must touch one file, stage the owned hunks with `git add -p`, then commit the
  reviewed index **without** a commit pathspec. Passing the file again to `git commit` defeats the
  partial-staging boundary. ([[wiki/sources/git-add-patch]])
- Prefer one owner per shared source file or separate worktrees. Locks protect runtime resources only
  when launchers enforce them; they do not prove Git hunk ownership.
- Verify the committed tree, not the dirty workspace, so uncommitted companions cannot hide an
  incomplete commit. Derive attribution from the diff rather than intended ownership.

## Related concepts

- [[wiki/concepts/research-discipline]] - immutable, inspected evidence rather than remembered state.
- [[wiki/moc/bsb-architecture]] - maintainer workflow for this Git-backed brain.

## Sources

- [[wiki/sources/git-commit-pathspec]]
- [[wiki/sources/git-add-patch]]
- [[wiki/sources/git-diff-review]]
- [[wiki/sources/maypaintworks-multi-agent-evidence]]
