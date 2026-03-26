# Graph-Based Data Modeling and Query System

This project provides a graph-first interface for exploring order-to-cash data with a FastAPI backend, a React frontend, SQLite for queryable storage, NetworkX for graph construction, and Gemini for natural-language-to-SQL and answer generation.

## Overview

The system has two separate deployable applications:

- `backend/`: FastAPI API, SQLite initialization, graph construction, Gemini-backed query flow
- `frontend/`: React + Vite application for graph visualization and chat-based querying

The backend loads structured business data from the `data/` directory, transforms it into a canonical relational model, stores that model in SQLite, builds a directed graph in memory, and exposes both graph APIs and a natural-language query API.

The frontend consumes those APIs to render a Cytoscape graph, inspect nodes, and ask grounded questions over the dataset.

## Architecture Decisions

### 1. Split frontend and backend deployments

The frontend and backend are intentionally separated:

- the frontend is static and suited to Vercel
- the backend is stateful at startup because it loads data, initializes SQLite, builds the graph, and talks to Gemini
- decoupling them keeps deployment concerns cleaner and avoids bundling the UI with API runtime concerns

This also makes local development simpler:

- frontend can run independently with `VITE_API_BASE_URL`
- backend can run independently with local or deployed data and environment settings

### 2. Canonical relational model on top of raw source data

The raw dataset is SAP-style partitioned `jsonl`, not immediately suited to direct querying from the frontend or LLM. The backend therefore transforms it into a smaller canonical schema:

- `customers`
- `products`
- `plants`
- `orders`
- `order_items`
- `deliveries`
- `invoices`
- `payments`

This decision reduces prompt complexity, keeps SQL generation narrower, and makes graph construction deterministic.

### 3. Build the graph once at startup

The graph is built once and cached in memory instead of rebuilding per request.

Reasoning:

- graph topology changes only when the underlying dataset changes
- graph reads should be fast for UI interactions
- startup work is acceptable because initialization is deterministic and bounded by dataset size

This produces quick responses for:

- full graph load
- node inspection
- subgraph extraction

## Why SQLite

SQLite was chosen over a larger database for this project because:

- the dataset is local and file-based
- setup is minimal for development and demos
- the LLM-generated SQL problem is simpler when the dialect is tightly constrained
- the app does not need multi-user write throughput
- deployment is easier than provisioning and managing a separate database service

SQLite fits this system well because the workload is primarily:

- startup ingestion
- read-only analytical queries
- deterministic joins across a moderate dataset

The backend explicitly blocks write operations from the LLM query path, so SQLite acts as a compact analytical store rather than an operational transactional database.

## Backend Flow

### Data initialization

`backend/database/init_db.py`:

- reads raw `jsonl` source directories from `DATA_DIR`
- derives canonical entities from raw business records
- creates SQLite tables
- replaces table contents on startup
- prints row counts for verification

### Graph construction

`backend/graph/builder.py`:

- reads canonical entities from SQLite
- builds a directed NetworkX graph
- stores metadata on nodes
- stores relationship type on edges
- exposes helpers for full graph, node neighbors, and subgraphs

### Query flow

`POST /api/query` follows this pipeline:

1. validate the question with guardrails
2. build a SQL-generation prompt with schema context
3. call Gemini to generate SQLite SQL
4. validate the SQL as read-only
5. execute the SQL against SQLite
6. build an answer-generation prompt using the raw results
7. call Gemini again to produce a grounded natural-language answer
8. return answer, SQL, raw results, and referenced node IDs

## LLM Prompting Strategy

The LLM layer uses a two-stage prompting approach.

### Stage 1: SQL generation

Goal:

- convert a user question into valid SQLite SQL only

Prompt includes:

- the canonical schema
- primary and foreign key structure
- explicit instruction to return SQL only
- restrictions against non-read-only statements
- example natural-language to SQL pairs

Why this design:

- schema grounding narrows hallucination risk
- examples improve query shape consistency
- SQL-only output makes validation and execution simpler

### Stage 2: answer generation

Goal:

- convert SQL results into a readable answer without inventing facts

Prompt includes:

- original user question
- SQL that was executed
- raw result rows serialized as JSON
- instruction to answer strictly from those rows

Why this design:

- the LLM never answers directly from user text alone
- the answer is downstream of actual database results
- this keeps the natural-language layer grounded in retrieved data

## Build Workflow

The implementation workflow for this project was also AI-assisted.

High-level process:

- the product/task definition was first explored in Claude
- Claude was used to reason about how the system should be implemented and what stack would fit the problem
- from that, separate build prompts were prepared for the backend and frontend
- those prompts were then executed through Codex CLI to implement the actual codebase

In practice, that means:

- Claude was used more for planning, decomposition, and prompt drafting
- Codex CLI was used for code generation, file editing, iteration, verification, and refinement inside the repository

This is not part of the application runtime architecture, but it is part of how the project was developed. The final code, structure, and deployment setup were still adjusted during implementation to account for real issues such as dataset shape, import paths, deployment constraints, UI iteration, and runtime integration with Gemini.

## Guardrails

Guardrails exist in two places.

### 1. Topic relevance guardrails

`backend/llm/guardrails.py` checks whether the query is about the supported business domain:

- orders
- deliveries
- invoices
- payments
- customers
- products
- billing
- logistics
- finance
- supply chain

It first uses keyword matching, then falls back to an LLM classification prompt when necessary.

If the query is off-topic, the system returns:

`This system is designed to answer questions related to the provided dataset only.`

### 2. SQL safety guardrails

Before any generated SQL is executed:

- only `SELECT` and `WITH` queries are allowed
- multiple statements are rejected
- write and schema-altering keywords are blocked

Examples of blocked behavior:

- `DROP`
- `DELETE`
- `UPDATE`
- `INSERT`
- `ALTER`
- `PRAGMA`
- transaction statements

This ensures the LLM is restricted to read-only analytics.

### 3. Retry-on-error behavior

If SQL generation produces invalid SQL or SQL that fails execution:

- the backend retries once
- the retry prompt includes the previous error

This improves resilience without allowing uncontrolled repeated attempts.

## Frontend Design Decisions

The frontend is structured around three concerns:

- left sidebar for graph context and stats
- center graph canvas for spatial exploration
- right chat panel for question answering

Key choices:

- Cytoscape for interactive graph rendering
- hooks (`useGraph`, `useChat`) for API and UI state separation
- environment-based API base URL for local/dev/prod portability
- graph highlight support driven by query results

The maximize/minimize control focuses on layout changes only. It does not rerun expensive graph layouts on every toggle, which keeps the UI responsive.

## Deployment Model

Recommended deployment:

- backend on Render
- frontend on Vercel

Why:

- frontend is a static build
- backend needs runtime environment variables, Gemini access, and dataset startup initialization

The frontend reads:

- `VITE_API_BASE_URL`

The backend reads:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `DATABASE_URL`
- `DATA_DIR`

## Tradeoffs and Limitations

- SQLite is simple but not ideal for large-scale concurrent production workloads
- the backend currently rebuilds the local database from source data on startup
- Gemini answer quality depends on the generated SQL being semantically correct
- SQL validation is conservative but still string-based, not full SQL parsing
- the deployed backend must have access to the `data/` directory or another data-loading mechanism

## Local Development

Backend:

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Future Improvements

- migrate from `google-generativeai` to the newer Google GenAI SDK
- add automated backend and frontend tests
- replace string-based SQL validation with parser-based validation
- move dataset loading to cloud storage or managed persistence for production
- add graph layout persistence so users keep stable visual positions across sessions
