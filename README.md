# 🧠 Open Pandas-AI - AI Data Analysis Agent

Intelligent agent for analyzing data with AI. Load a CSV/Excel file, ask your questions in natural language, get answers with automatically generated code.

## ✨ Latest Updates

**Phase 2 - Hybrid Dictionary System** (NEW):
- Automatic dataset type detection (12+ domains)
- Predefined dictionaries for E-commerce, CRM, HR, Finance, etc.
- Optional enrichment with intuitive UI
- LLM integration for better business context
- Estimated response quality improvement: +15-25%

**Phase 1 - Response Quality**:
- Detection of 16 analytical intentions
- Intelligent result validation
- Improvement suggestions
- Quality scoring

## 🚀 Features

## Getting Started

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Export your Codestral key:

```bash
export MISTRAL_API_KEY="sk-..."
```

3. Launch the Streamlit interface:

```bash
streamlit run app.py
```

4. Upload a CSV, ask a question ("What are the 5 countries with the most sales?")

## Features

- Automatic Python/Pandas code generation via Codestral
- Local execution, results displayed directly
- Compatible with all questions about your CSV files (NL2Pandas)
- Intelligently formatted results (table, list, text...)

## MVP Limitations

- Ephemeral Docker sandbox available (enable via USE_DOCKER_SANDBOX=true)
- **No automatic graphical visualization**
- **No automatic error correction**
- **No multi-DataFrame joins**
- Recommended for use in test environment!

---

Developed with ❤️ for AI and data enthusiasts.
Credits: [Mistral AI](https://mistral.ai/) + Pandas + Streamlit

## Sandbox and Security

- Generated Pandas code is executed in an isolated subprocess (`core.sandbox_runner`).
- AST analysis is reinforced to block imports, dangerous introspection and system access.
- Adjust the maximum delay via the `SANDBOX_TIMEOUT_SECONDS` environment variable.

## Automated Tests

```bash
pytest
```

Tests cover utilities (`core/utils.py`) and a complete analysis flow with a mocked LLM.

## Docker Compose Deployment

1. Copy `.env.example` to `.env` and fill in your secrets (Mistral key, Postgres URL).
2. Launch everything:
   ```bash
   docker compose up --build
   ```
3. Streamlit is available at http://localhost:8501.
4. The `db` database exposes `postgresql+psycopg2://postgres:postgres@db:5432/openpanda` by default. Modify these values for a production environment.

## Dependency Management

- `requirements.txt` pins versions for reproducible builds.
- To update properly: install `pip-tools` then `pip-compile requirements.in` (to introduce if needed) to regenerate `requirements.txt`.
- For more advanced workflows or mono-repo, Poetry remains a viable option, but is not necessary for this MVP.


## Enhanced Security with Docker

### Secure Execution with Ephemeral Containers

The project now uses **ephemeral Docker containers** for executing AI-generated code:

- ✅ Complete isolation: each execution in a dedicated container
- ✅ Auto-destruction: containers automatically deleted after use
- ✅ Resource limits: CPU/memory/network controlled
- ✅ Non-privileged user: execution without administrator rights

### Configuration

1. Build the sandbox image:
```bash
chmod +x scripts/build-sandbox.sh
./scripts/build-sandbox.sh
```

2. Enable Docker mode:
```bash
export USE_DOCKER_SANDBOX=true
docker compose up --build
```

3. Fallback mode: If Docker is not available, the system automatically uses the old subprocess mode.

### Security Architecture

```
User Question
    ↓
AI Generated Code
    ↓
AST Validation (code_security.py)
    ↓
Ephemeral Docker Container
    ├── Network isolation (network_mode=none)
    ├── Resource limits (512MB RAM, 50% CPU)
    ├── Non-privileged user
    └── Auto-destruction after execution
    ↓
Secure Result
```

### Environment Variables

- `USE_DOCKER_SANDBOX=true` : Enables Docker execution
- `SANDBOX_TIMEOUT_SECONDS=30` : Execution timeout
- `SANDBOX_IMAGE=openpanda-sandbox:latest` : Image to use
