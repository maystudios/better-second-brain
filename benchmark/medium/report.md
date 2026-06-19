# Benchmark Report — Model Context Protocol (MCP), "medium" set

Two knowledge-base methods scored strictly against a gold set of 10 questions.
Each arm scored on three 0-2 dimensions per question: correctness, citation, faithfulness.
Per-dimension scores are averaged across the 10 questions (0-2 each); arm total = sum of the three averages (0-6).

## Per-question scores

| Q | Type | Vanilla (corr/cite/faith) | BSB (corr/cite/faith) | Note |
|---|------|---------------------------|------------------------|------|
| 1 | recall | 2 / 1 / 2 | 2 / 2 / 2 | Both nail USB-C. BSB cites exact `introduction` source; vanilla vague. |
| 2 | recall | 2 / 1 / 2 | 2 / 2 / 2 | Tools/Resources/Prompts correct both. BSB cites exact `architecture` URL; vanilla cites wrong page name, no URL. |
| 3 | detail | 2 / 1 / 2 | 2 / 2 / 2 | JSON-RPC 2.0 correct both. BSB exact cite; vanilla vague. |
| 4 | detail | 2 / 1 / 2 | 0 / 0 / 2 | Vanilla wins. Gold = -32002; vanilla recalled it. BSB gate over-abstained ("wiki does not say"), only mentions -32602. |
| 5 | detail | 2 / 1 / 2 | 2 / 2 / 2 | Mcp-Session-Id + 404 correct both. BSB exact cite; vanilla vague. |
| 6 | detail | 2 / 1 / 2 | 2 / 2 / 2 | 2025-03-26 correct both. BSB exact cite; vanilla vague. |
| 7 | detail | 2 / 1 / 2 | 2 / 2 / 2 | `mcp` + `uv add "mcp[cli]"` correct both. BSB exact cite; vanilla vague. |
| 8 | freshness | 2 / 1 / 2 | 2 / 2 / 2 | 2025-11-25 correct both. BSB exact cite; vanilla vague. |
| 9 | freshness | 2 / 1 / 2 | 2 / 2 / 2 | v2 pre-alpha / v1.x prod correct both. BSB exact cite; vanilla vague. |
| 10 | unsupported | 2 / 1 / 2 | 2 / 2 / 2 | Both reject premise. BSB lists 7 maintained servers + exact `servers` URL; vanilla no list, no URL. |

## Dimension averages

| Dimension | Vanilla | BSB |
|-----------|---------|-----|
| Correctness | 2.00 | 1.80 |
| Citation | 1.00 | 1.80 |
| Faithfulness | 2.00 | 2.00 |
| Total (0-6) | 5.00 | 5.60 |

## Summary

BSB wins, 5.60 vs 5.00 (+12.0%).

- Correctness: vanilla is actually ahead (2.00 vs 1.80) — it answered all 10 from memory. BSB's only loss is Q4, where its retrieval gate abstained on the -32002 resource-not-found code (a genuine, answerable fact). Clearest case of the gate hurting BSB.
- Citation is BSB's entire margin (1.80 vs 1.00). On all 9 answered questions BSB cites the exact gold source URL; vanilla gives vague "wiki <Page>" refs with no URL, and on Q2/Q10 the page name does not even match the gold source.
- Faithfulness ties at 2.00. Neither fabricated. BSB's Q4 abstention is faithful but under-informative; vanilla's confident -32002 happened to be right.
- Net: vanilla = reliably correct but unverifiable; BSB = matched every substantive answer plus precise checkable links. The one vanilla win (Q4) was BSB over-abstaining on a recallable detail.
