# Architecture

## Overview

ContextFusion is built as a universal context middleware that processes heterogeneous
data sources into optimized provider-agnostic context packets.

```
Ingest → Normalize → Represent → Retrieve → Score → Optimize → Assemble → Compile
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

### Scoring Layer

Computes utility and risk scores:
- **Utility**: Based on retrieval, trust, freshness, structure, diversity
- **Risk**: Based on hallucination proxy, staleness, privacy

### Allocation Layer

Optimizes context selection:
- **BudgetManager**: Manages token budgets across categories
- **KnapsackOptimizer**: Solves 0/1 knapsack for optimal selection
- **PortfolioSelector**: Orchestrates selection process

### Retrieval Layer

Two-stage retrieval before knapsack optimization:
- **BM25Retriever**: lexical top-100 candidate retrieval
- **SimpleReranker**: rerank to top-20 before optimization

### IR + Assembly Layers

- **ContextPacket IR** (`ir/context_packet.py`): canonical selected-block packet
- **Compiler** (`assembly/compiler.py`): provider-specific message/prompt compilation

### Providers Layer

Adapter system under `providers/`:
- OpenAI
- Anthropic
- Ollama
- OpenAI-compatible endpoints (Grok/Kimi/DeepSeek/Together/Groq style APIs)

### Agent + MCP + Integrations

- **agents/agent_runner.py**: agent-step orchestration with context optimization
- **mcp_server/**: MCP-style tools/resources server
- **integrations/**: LangChain and LlamaIndex retriever wrappers
- **precompute/runner.py**: offline precompute for summaries/tokens/hashes/embeddings

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
3. **Represent**: Generate alternative representations
4. **Retrieve**: BM25 top-100 and rerank top-20 (when query is provided)
5. **Score**: Compute utility and risk
6. **Optimize**: Select optimal subset with knapsack
7. **Assemble**: Build final context and ContextPacket IR
8. **Compile**: Convert packet to provider-facing chat/prompt payloads
