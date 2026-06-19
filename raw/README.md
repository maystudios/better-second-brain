# raw/ — your source material

This folder holds the **immutable sources** the brain is built from. The LLM **reads** from here and **never
writes** here (the one exception: `raw/assets/`, where Obsidian's Web Clipper drops downloaded images).

Drop things in and tell the agent to *ingest* them. Suggested sub-folders (create as needed):

```
raw/
├── articles/      clipped web articles (Obsidian Web Clipper → markdown)
├── papers/        PDFs
├── notes/         your own notes, pasted text
├── transcripts/   talk / video / podcast transcripts
├── videos/        local media (the .mp4s are git-ignored; their summaries are kept)
└── assets/        images referenced by pages (![[raw/assets/x.png]])
```

Every file you ingest gets a paired page in `wiki/sources/` (the research-discipline rule, `CLAUDE.md` §1.5).
Curating good sources is *your* job; everything downstream is the agent's.
