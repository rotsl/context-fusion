# Architecture

## Overview

ContextFusion is built around a pipeline architecture that processes heterogeneous data sources into optimized LLM context.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Ingest    │───▶│  Normalize  │───▶│  Represent  │───▶│   Score     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                  │
                                                                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Assemble  │◀───│  Portfolio  │◀───│  Knapsack   │◀───│  Utility    │
│   Context   │    │   Select    │    │  Optimize   │    │   & Risk    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
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

### Memory Layer

Manages persistent memory:
- **MemoryStore**: JSONL-based storage
- **MemoryCompactor**: Removes duplicates and old entries
- **RetentionPolicy**: Enforces retention rules

### Interface Layer

User-facing entry points:
- **CLI (`cpo`)**: Command-line operations for ingest/run/plan/ablate
- **Web UI (`cpo ui`)**: Local browser-based visualization over pipeline outputs

## Data Flow

1. **Ingest**: Files → RawSegments
2. **Normalize**: RawSegments → ContextBlocks
3. **Represent**: Generate alternative representations
4. **Score**: Compute utility and risk
5. **Optimize**: Select optimal subset
6. **Assemble**: Build final context string
