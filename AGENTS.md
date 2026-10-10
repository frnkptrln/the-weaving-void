# Working in this repository

An executable laboratory for texts that carry a program: weaves between prose
surface and executable thread, with the esolang archive they grew out of.

## Checks

```bash
python -m pip install -r Bloom/requirements.txt
python scripts/smoke_test.py                       # every archived language plus the whole Subtext suite
python -m unittest discover -s weaves/subtext -t .
```

## Rules

- A committed surface comes with its witness file; both must reproduce from
  the documented command before a pull request is opened.
- Sentences in a bank are authored, not generated; a constructor selects.
- The esolang archive stays runnable; adding a weave never breaks a language.

## Working alongside other agents

Frank and two agents (Claude and ChatGPT/Codex) work in this repository, often
at the same time. The repository itself is the only channel between them.

- Work on your own branch (`codex/…`, `claude/…`). Open a draft pull request
  as soon as you start and list the files you expect to touch. Before you
  branch, read the open pull requests and keep away from their files. Never
  push to another agent's branch, and never to `main` directly.
- A pull request says what changed, why, what was checked (the commands and
  their results) and what remains unverified. Fix a failing check; do not
  weaken or skip it.
- No author trailers (`Co-Authored-By` and the like) in commits or pull
  requests. The commit author is enough.
- No status files, task lists or progress notes in the repository. The pull
  requests and the history are the record.
- Frozen material (below) is not edited in place. It changes only through the
  mechanism this repository defines for it, or not at all.
