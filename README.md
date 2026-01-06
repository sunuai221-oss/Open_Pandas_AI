# 🚀 Open Pandas-AI

<div align="center">

**Intelligent AI-powered data analysis agent**

Ask questions in natural language and get Python/Pandas code generated and executed securely — 100% local or cloud.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/sunuai221-oss/Open_Pandas_AI/actions/workflows/python-tests.yml/badge.svg)](https://github.com/sunuai221-oss/Open_Pandas_AI/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#features) · [Quick Start](#quick-start) · [LLM Providers](#llm-providers) · [Documentation](#documentation) · [Contributing](#contributing)

</div>

---

## ⚡ Quick Start

```bash
# Clone and install
git clone https://github.com/sunuai221-oss/Open_Pandas_AI.git
cd Open_Pandas_AI
pip install -r requirements.txt

# Run with LM Studio (100% local, no API key needed)
export LLM_PROVIDER=lmstudio
streamlit run app.py
```

Then open **http://localhost:8501**, upload a CSV/Excel file, and ask questions!

---

## 📚 Table of Contents

- [Quick Start](#quick-start)
- [Overview](#overview)
- [Features](#features)
- [LLM Providers](#llm-providers)
- [Installation](#getting-started)
- [Architecture](#architecture)
- [Security](#security)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Testing](#testing)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Features in Detail](#features-in-detail)
- [Performance](#performance)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [Tech Stack](#tech-stack)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Support](#support)

---

<a id="overview"></a>
## 🧭 Overview

**Open Pandas-AI** transforms natural language questions into Python/Pandas code, executes it in a secure sandbox, and displays formatted results. It is built for analysts, researchers, and teams who want fast insights without hand-writing data code.

<!-- Add your screenshot here -->
<!-- ![Open Pandas-AI Demo](docs/screenshot.png) -->

**Version**: 2.0  
**Framework**: Streamlit (Python 3.11)

### Latest Updates

**Phase 2 - Hybrid Dictionary System**:
- Automatic dataset type detection (12+ domains)
- Predefined dictionaries for E-commerce, CRM, HR, Finance, and more
- Optional enrichment through the UI
- Better business context for the LLM
- Estimated response quality improvement: 15-25%

**Phase 1 - Response Quality**:
- Detection of 16 analytical intentions
- Intelligent result validation
- Improvement suggestions
- Quality scoring

---

<a id="features"></a>
## ✨ Features

- **Natural Language to Pandas**: Ask questions in plain language, get Python/Pandas code
- **Multi-LLM Support**: Codestral (cloud), Ollama (local), LM Studio (local)
- **Intention Detection**: Automatically detects 16+ analysis intents
- **Hybrid Data Dictionary**: Auto-detect + manual enrichment for better context
- **Secure Code Execution**: Docker sandbox or subprocess isolation with AST validation
- **Conversational Memory**: Maintains context across questions
- **Result Validation**: Quality scoring and suggestions
- **Excel Integration**: Multi-sheet support and formatted exports
- **Multi-page UI**: Home, Data Explorer, Agent, History, Settings, Dashboard

---

<a id="llm-providers"></a>
## 🧠 LLM Providers

Open Pandas-AI supports multiple providers for code generation:

### 1) Codestral (Mistral AI) - Free API (Recommended)

- **Type**: Cloud API (free tier available)
- **Setup**: Get your API key from [Mistral AI](https://mistral.ai/)
- **Configuration**:
  ```bash
  export MISTRAL_API_KEY="your-api-key-here"
  export LLM_PROVIDER="codestral"
  export LLM_MODEL="codestral-latest"
  ```
- **Best for**: Quick start and production use

### 2) Ollama (Local)

- **Type**: Local models (runs on your machine)
- **Setup**: Install [Ollama](https://ollama.ai/) and download a model
- **Configuration**:
  ```bash
  export LLM_PROVIDER="ollama"
  export LLM_MODEL="codestral-latest"
  export OLLAMA_BASE_URL="http://localhost:11434"
  ```
- **Best for**: Privacy-sensitive data and offline work

### 3) LM Studio (Local)

- **Type**: Local server (runs on your machine)
- **Setup**: Install [LM Studio](https://lmstudio.ai/) and start a local server
- **Configuration**:
  ```bash
  export LLM_PROVIDER="lmstudio"
  export LLM_MODEL="codestral-latest"
  export LMSTUDIO_BASE_URL="http://localhost:1234"
  ```
- **Best for**: Model experimentation and offline use

> You can switch providers at runtime via the Settings page in the UI.

---

<a id="getting-started"></a>
## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker (optional, for secure sandbox execution)
- PostgreSQL (optional, for persistent storage)

### Installation

1) **Clone the repository**:
   ```bash
   git clone https://github.com/sunuai221-oss/Open_Pandas_AI.git
   cd Open_Pandas_AI
   ```

2) **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3) **Configure your LLM provider** (choose one):

   **Option A: Codestral (Recommended)**
   ```bash
   export MISTRAL_API_KEY="your-api-key-here"
   export LLM_PROVIDER="codestral"
   export LLM_MODEL="codestral-latest"
   ```

   **Option B: Ollama**
   ```bash
   ollama pull codestral-latest
   export LLM_PROVIDER="ollama"
   export LLM_MODEL="codestral-latest"
   export OLLAMA_BASE_URL="http://localhost:11434"
   ```

   **Option C: LM Studio**
   ```bash
   export LLM_PROVIDER="lmstudio"
   export LLM_MODEL="codestral-latest"
   export LMSTUDIO_BASE_URL="http://localhost:1234"
   ```

4) **Launch the app**:
   ```bash
   streamlit run app.py
   ```

5) **Open your browser**: `http://localhost:8501`

---

<a id="architecture"></a>
## 🧩 Architecture

The project follows a layered architecture:

```
UI (Streamlit pages)
  -> components/ (reusable UI)
  -> core/ (business logic)
  -> agents/ (domain agents)
  -> db/ (persistence)
```

Key components:
- **Session Manager**: Centralized state across pages
- **LLM Integration**: Multi-provider abstraction
- **Intention Detector**: 16+ analysis intentions
- **Prompt Builder**: Multi-level prompt enrichment
- **Secure Executor**: Docker or subprocess sandbox with validation
- **Data Dictionary Manager**: Hybrid dictionary system
- **Conversational Memory**: Context preservation across exchanges

See `TECHNICAL_REPORT.md` for deeper architecture details.

---

<a id="security"></a>
## 🔐 Security

### Multi-Level Security

1. **AST Validation**: Static code analysis blocks dangerous operations
2. **Execution Isolation**:
   - **Docker mode** (recommended): ephemeral containers with isolation
   - **Subprocess mode**: isolated local execution
3. **Resource Limits**: Memory/CPU/timeout controls (default timeout is 10s in code, 30s in docker-compose)
4. **Environment Cleanup**: API secrets removed from execution environment
5. **Non-Privileged Execution**: Code runs with restricted permissions

### Security Flow

```
User Question
  -> LLM Generated Code
  -> AST Validation
  -> Sandboxed Execution
  -> Safe Result
```

### Enable Docker Sandbox

1) **Build the sandbox image**:
   ```bash
   chmod +x scripts/build-sandbox.sh
   ./scripts/build-sandbox.sh
   ```

2) **Enable Docker mode**:
   ```bash
   export USE_DOCKER_SANDBOX=true
   export SANDBOX_TIMEOUT_SECONDS=30
   ```

---

<a id="usage-examples"></a>
## 💡 Usage Examples

### Basic Usage

1) Upload a CSV or Excel file
2) Ask a question on the Agent page:
   ```text
   What are the 5 countries with the most sales?
   ```
3) The AI generates and runs code, then displays results
4) Ask follow-up questions and export results to Excel

### Example Questions

- "Show me the top 10 products by revenue"
- "What is the average age by department?"
- "Create a pivot table of sales by region and product"
- "Find all orders with missing customer information"
- "Calculate the correlation between price and sales"

---

<a id="configuration"></a>
## ⚙️ Configuration

### Environment Variables

**Required**:
- `MISTRAL_API_KEY` (only if using Codestral)

**Optional**:
- `LLM_PROVIDER`: `codestral` | `ollama` | `lmstudio` (default: `lmstudio`)
- `LLM_MODEL`: model name (default: `codestral-latest`)
- `USE_DOCKER_SANDBOX`: `true` | `false` (default: `false`)
- `SANDBOX_TIMEOUT_SECONDS`: execution timeout (default: `10`)
- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://localhost:11434`)
- `LMSTUDIO_BASE_URL`: LM Studio server URL (default: `http://localhost:1234`)
- `DATABASE_URL`: PostgreSQL connection string (for persistent storage)
- `OFFLINE_ONLY`: `true` to hide cloud providers in the UI (local-only mode)

### UI Settings

Configure via the Settings page:
- LLM provider and model
- User level (beginner/expert)
- Language
- Theme
- Code display
- Display row limits

---

<a id="testing"></a>
## 🧪 Testing

Run the test suite:

```bash
pytest
```

With coverage (as in CI):

```bash
pytest --cov=. --cov-report=xml --cov-report=html
```

---

<a id="docker-compose-deployment"></a>
## 🐳 Docker Compose Deployment

For a full setup with PostgreSQL:

1) **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2) **Edit `.env`**:
   ```env
   MISTRAL_API_KEY=your-api-key-here
   LLM_PROVIDER=codestral
   LLM_MODEL=codestral-latest
   USE_DOCKER_SANDBOX=true
   SANDBOX_TIMEOUT_SECONDS=30
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/openpanda
   ```

3) **Launch**:
   ```bash
   docker compose up --build
   ```

4) **Open**: `http://localhost:8501`

---

<a id="features-in-detail"></a>
## 🔎 Features in Detail

### Analytical Intentions

The system detects and optimizes for:
Filtering, Sorting, Statistics, Aggregation, Time Series, Join, Anomaly Detection,
Transformation, Duplicate Handling, Missing Values, Segmentation, Ranking,
Comparison, Pivot Table, Pattern Detection, Export.

### Hybrid Data Dictionary

- Auto-detects business domains
- Generates dictionary if no match is found
- UI enrichment for better context
- Improves LLM response quality by 15-25%

### Business Agents

Domain-aware agents customize prompts by data type:

| Domain | Agent | Typical tasks |
|--------|-------|---------------|
| Finance | FinanceAgent | Transactions, reporting, reconciliation |
| E-commerce | EcommerceAgent | Sales analysis, AOV, segmentation |
| HR | HRAgent | Tenure, salary benchmarks |
| CRM | CRMAgent | Pipeline analysis, lead scoring |
| Generic | GenericAgent | Default fallback |

### Conversational Memory

- Keeps context across questions
- Stores exchange history with metadata
- Generates optimized context for prompts

---

<a id="performance"></a>
## ⚡ Performance

Typical processing times:
- Code generation: 2-5s (provider-dependent)
- Code execution: <1s (average datasets)
- Validation: <0.5s
- **Total**: 3-7s per question

Recommended limits:
- Data size: <1M rows
- Timeout: 10-30s (configurable)
- Memory: 512 MB per execution

---

<a id="limitations"></a>
## 🚧 Limitations

- Single DataFrame at a time (no automatic multi-file joins)
- Manual error correction for failed generations
- Limited visualization automation (planned)
- Best performance with datasets <1M rows

---

<a id="roadmap"></a>
## 🗺️ Roadmap

- [ ] Multi-DataFrame support with automatic joins
- [ ] Automatic error correction
- [ ] Automatic visualization generation
- [ ] Result caching
- [ ] Additional export formats (JSON, Parquet)
- [ ] Session collaboration/sharing
- [ ] REST API
- [ ] Plugin system

---

<a id="tech-stack"></a>
## 🧰 Tech Stack

**Backend**:
- Python 3.11
- Streamlit 1.45.1
- Pandas 2.2.3
- SQLAlchemy 2.0.41
- Docker 7.0.0

**LLM Integration**:
- Codestral (Mistral AI)
- Ollama
- LM Studio

**Security**:
- AST validation
- Docker sandbox
- psutil resource monitoring

**UI/UX**:
- Streamlit components
- Altair 5.5.0
- Matplotlib 3.10.3

---

<a id="documentation"></a>
## 📖 Documentation

- **Technical Report**: `TECHNICAL_REPORT.md`
- **Architecture**: `TECHNICAL_REPORT.md#-general-architecture`
- **Security**: `TECHNICAL_REPORT.md#-security`
- **Components**: `TECHNICAL_REPORT.md#-key-components`

---

<a id="contributing"></a>
## 🤝 Contributing

Contributions are welcome.

1) Fork the repository
2) Create a feature branch (`git checkout -b feature/amazing-feature`)
3) Make your changes
4) Add tests when applicable
5) Commit (`git commit -m "Add amazing feature"`)
6) Push (`git push origin feature/amazing-feature`)
7) Open a Pull Request

### Development Setup

```bash
git clone https://github.com/sunuai221-oss/Open_Pandas_AI.git
cd Open_Pandas_AI

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install pytest black flake8
pytest
black .
```

### Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to public functions/classes
- Write tests for new features

---

<a id="license"></a>
## 📄 License

This project is licensed under the MIT License. See `LICENSE`.

---

<a id="credits"></a>
## 🙏 Credits

Developed with care for AI and data enthusiasts.

**Powered by**:
- [Mistral AI](https://mistral.ai/)
- [Ollama](https://ollama.ai/)
- [LM Studio](https://lmstudio.ai/)
- [Pandas](https://pandas.pydata.org/)
- [Streamlit](https://streamlit.io/)

---

<a id="support"></a>
## 🆘 Support

- **Issues**: https://github.com/sunuai221-oss/Open_Pandas_AI/issues
- **Discussions**: https://github.com/sunuai221-oss/Open_Pandas_AI/discussions
- **Email**: sunuai221@gmail.com

---

<div align="center">

**Version**: 2.0  
**Last Updated**: January 2026

Made with ❤️ by the Open Pandas-AI team

</div>
