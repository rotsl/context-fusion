# Architecture

## Overview

ContextFusion is built as a universal context middleware that processes heterogeneous
data sources into optimized provider-agnostic context packets.

```
Ingest -> Normalize -> Canonical IR -> Precompute -> Dedup/Fingerprint
-> Query Classify -> Candidate Retrieval -> Fast Rerank -> Budget Planner
-> Context Compression -> Delta Fusion -> Provider Adapter -> Cache-Aware Assemble
```

## Components

### Ingestion Layer

The ingestion layer handles multiple file formats:

- **TextLoader**: `.txt`, `.log` files
- **PDFLoader**: `.pdf` files (via pdfminer.six)
- **DocxLoader**: `.docx` files (via python-docx)
- **CSVLoader**: `.csv`, `.tsv` files (via pandas)
- **JSONLoader**: `.json`, `.jsonl` files
- **MarkdownLoader**: `.md` files
- **ImageLoader**: `.png`, `.jpg`, etc. (via OCR)
- **CodeLoader**: Source code files

### Normalization Layer

Converts `RawSegment` objects to `ContextBlock` objects with:
- Unique IDs
- Token counts
- Metadata extraction
- Trust and freshness scores

### Representation Layer

Generates alternative representations:
- `full_text`: Original content
- `bullet_summary`: Key points as bullets
- `structured_json`: JSON with metadata
- `extracted_facts`: Key facts only
- `citation_pointer`: Compact reference
- `table_summary`: Table structure summary
- `code_signature_summary`: Function/class signatures
- Task-aware compact families:
  - QA variants (`extractive_span`, `bullet_summary_3`, `json_fact`, `citation_only`, `outline`)
  - Code variants (`signature_only`, `docstring_only`, `changed_region`, `imports_plus_signature`)
  - Agent variants (`state_summary`, `constraint_delta`, `working_memory_brief`)

### Scoring Layer

Computes utility and risk scores:
- **Utility**: Based on retrieval, trust, freshness, structure, diversity
- **Risk**: Based on hallucination proxy, staleness, privacy

### Allocation + Planning Layer

Optimizes context selection:
- **BudgetManager**: Manages token budgets across categories
- **KnapsackOptimizer**: Legacy 0/1 knapsack foundation
- **BudgetPlanner**: Multi-objective latency-aware planner with value-density ranking
- **PortfolioSelector**: Compatibility path and score orchestration

### Retrieval Layer

Two-stage retrieval before knapsack optimization:
- **BM25Retriever**: lexical top-100 candidate retrieval
- **SimpleReranker**: rerank to top-20/25 before planning
- **QueryClassifier**: classify task mode (chat/qa/code/agent)
- **Metadata filters**: source type, freshness, tags, path filters

### IR + Assembly Layers

- **ContextPacket IR** (`ir/context_packet.py`): canonical selected-block packet
- **CacheSegment IR** (`ir/cache_segment.py`): stable/dynamic cache partition
- **ContextDelta IR** (`ir/delta_packet.py`): incremental packet updates
- **Compiler** (`assembly/compiler.py`): provider-aware packers (`chat/qa/code/agent`)
- **Compression** (`compression/`): citation-map, JSON minify, schema prune

### Providers Layer

Adapter system under `providers/`:
- OpenAI
- Anthropic
- Ollama
- OpenAI-compatible endpoints (Grok/Kimi/DeepSeek/Together/Groq style APIs)
- Provider capability flags:
  - tool support
  - structured output support
  - prompt caching support
  - local vs remote

### Agent + MCP + Integrations

- **agents/agent_runner.py**: agent-step orchestration with context optimization
- **fusion/**: packet diff + delta fusion for repeated turns
- **mcp_server/**: MCP-style tools/resources server
- **integrations/**: LangChain and LlamaIndex retriever wrappers
- **precompute/**: offline precompute store for summaries/tokens/fingerprints/variants/features

### Memory Layer

Manages persistent memory:
- **MemoryStore**: JSONL-based storage
- **MemoryCompactor**: Removes duplicates and old entries
- **RetentionPolicy**: Enforces retention rules

### Interface Layer

User-facing entry points:
- **CLI (`cpo`)**: ingest/run/plan/compile/precompute/serve-mcp/benchmark-latency/ablate
- **Web UI (`cpo ui`)**: Local browser-based visualization over pipeline outputs

## Data Flow

1. **Ingest**: Files → RawSegments
2. **Normalize**: RawSegments → ContextBlocks
3. **Precompute + Dedup**: Reuse cache or build deterministic compact variants/fingerprints
4. **Classify + Retrieve**: classify query, retrieve top-100, rerank top-20/25
5. **Score**: Compute utility/risk and representation-level costs
6. **Plan**: select one compact representation per block under budget
7. **Assemble**: build `ContextPacket` + `CacheSegment` set
8. **Delta**: compute `ContextDelta` in agent loops
9. **Compile**: emit provider-ready request payloads
