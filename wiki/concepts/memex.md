---
type: concept
name: Memex
aliases:
  - memex
  - Bush's memex
  - associative trails
tags:
  - knowledge-management
  - prior-art
  - hypertext
  - second-brain
sources:
  - "[[wiki/sources/karpathy-llm-wiki]]"
created: 2026-06-19
updated: 2026-06-19
status: complete
---

# Memex

The memex is a hypothetical personal information device proposed by Vannevar Bush in his essay "As We May Think," published in *The Atlantic Monthly* in July 1945. Bush imagined a desk-like apparatus in which a person could store books, records, and communications on microfilm and consult them rapidly - "an enlarged intimate supplement to his memory." Its defining idea was the **associative trail**: a way of linking arbitrary records into chains that mirror how the mind associates, rather than forcing retrieval through rigid indexes. As the intellectual ancestor of hypertext and of the modern linked knowledge base, the memex prefigures both wikilinks and the LLM wiki pattern's emphasis on connections that are "already there."

## How it shows up

Bush's design anticipated, in mechanical form, the moves a linked second brain makes in software.

- **Personal augmentation of memory.** The memex was framed as a private extension of one person's recall - the same goal as a personal knowledge base built for "topics of research interest."
- **Associative trails.** Users could build "a new linear sequence of microfilm frames across any arbitrary sequence," chaining records together with their own annotations and branching "side trails." This is the conceptual root of the hyperlink: a durable, user-made connection between two pieces of content.
- **Trails as shareable artifacts.** Bush imagined trails being saved and passed to colleagues, anticipating the idea that the *structure of links* - not just the documents - is itself valuable knowledge worth preserving.
- **Association over indexing.** The memex deliberately replaced hierarchical indexing with connection-by-association, the same instinct behind a wiki whose value lives in its cross-references.

The unrealized hardware matters less than the idea: knowledge becomes more useful when the trails between items are first-class, persistent objects. That premise carries directly into the Zettelkasten's linked cards and into the LLM wiki, where cross-references and flagged contradictions are written down once and reused.

## Related concepts

- [[wiki/concepts/zettelkasten]] - the contemporaneous prior art that realized associative linking on paper cards.
- [[wiki/concepts/llm-wiki-pattern]] - the modern descendant, with an LLM maintaining the trails.
- [[wiki/concepts/knowledge-graph-graphrag]] - graphs make the associative trails explicit and traversable.
- [[wiki/moc/second-brain-pattern]] - the map of content for this lineage.

## Sources

- "Memex," Wikipedia. https://en.wikipedia.org/wiki/Memex (secondary; source of the device description, the "enlarged intimate supplement to his memory" phrasing, the associative-trail mechanism and the "new linear sequence of microfilm frames across any arbitrary sequence" wording, and the side-trails/sharing features). The primary essay - Vannevar Bush, "As We May Think," *The Atlantic*, July 1945, https://www.theatlantic.com/magazine/archive/1945/07/as-we-may-think/303881/ - was not directly fetchable from this environment, so its claims are corroborated here via the Wikipedia summary.
- [[wiki/sources/karpathy-llm-wiki]] - Andrej Karpathy, "LLM Wiki" gist. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f (primary, for the modern pattern this prior art anticipates; the "cross-references are already there" framing).
