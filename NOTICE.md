# Source provenance

Copyright 2026 Tim Warner. The code is released under the MIT license included in this package.
Pearson names, logos, and template elements retain their respective ownership and usage terms.

The incident starters adapt the official-SDK teaching pattern in Tim Warner's Context Engineering with MCP course.
The memory reference application borrows the four-role teaching design from WARNERCO Schematica:
working scratchpad, append-only episodic events, durable semantic facts, and versioned procedures.
This is a small independent reference implementation. It does not copy learner data,
credentials, databases, recordings, private client materials, or publisher correspondence.

For the larger vector/graph-backed implementation:
https://github.com/timothywarner-org/context-engineering/tree/main/src/warnerco/backend

Primary conceptual source: Sumers et al., Cognitive Architectures for Language Agents, 2024.
https://arxiv.org/abs/2309.02427

The memory-mcp storage adapter derives from Tim Warner's Copilot Memory Store,
commit 6f6f8fba9f0fa6f3221ed52d4fb1570f8fba3896, src/memoryStore.ts.
Its original MIT notice is preserved in [memory-mcp/LICENSE.upstream](memory-mcp/LICENSE.upstream).
Source: https://github.com/timothywarner-org/copilot-memory-store
The adaptation removes cloud summarization and destructive operations, validates
storage and input, removes recency-only relevance, and reports bounded selection accurately.
