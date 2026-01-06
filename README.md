# 🧠 Open Pandas-AI

<div align="center">

**Intelligent AI-powered data analysis agent**

Ask questions in natural language, get Python/Pandas code automatically generated and executed securely.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) • [Installation](#-getting-started) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [LLM Providers](#-llm-providers)
- [Getting Started](#-getting-started)
- [Architecture](#-architecture)
- [Security](#-security)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-docker-compose-deployment)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Open Pandas-AI** is an intelligent web application that transforms natural language questions into Python/Pandas code, executes it securely, and displays formatted results. Perfect for data analysts, researchers, and anyone who wants to analyze data without writing code.

**Version**: 2.0  
**Framework**: Streamlit (Python 3.11)

### ✨ Latest Updates

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

---

## 🚀 Features

- **🤖 Natural Language to Pandas**: Ask questions in plain language, get Python/Pandas code
- **🔌 Multi-LLM Support**: Choose between Codestral (free API), Ollama (local), or LM Studio (local)
- **🎯 Intelligent Intention Detection**: Automatically detects 16+ analytical intentions (filtering, aggregation, pivot tables, etc.)
- **📚 Hybrid Data Dictionary**: Automatic detection + manual enrichment for better context
- **🔒 Secure Code Execution**: Docker sandbox or subprocess isolation with AST validation
- **💭 Conversational Memory**: Maintains context across questions
- **✅ Result Validation**: Automatic quality scoring and suggestions
- **📊 Excel Integration**: Multi-sheet support, professional export formatting
- **📱 Multi-page Interface**: Home, Data Explorer, Agent, History, Settings, Dashboard

---

## 🤖 LLM Providers

Open Pandas-AI supports multiple LLM providers for code generation:

### 1. Codestral (Mistral AI) - **Free API** ⭐ Recommended

- **Type**: Cloud API (free tier available)
- **Setup**: Get your free API key from [Mistral AI](https://mistral.ai/)
- **Configuration**:
  ```bash
  export MISTRAL_API_KEY="your-api-key-here"
  export LLM_PROVIDER="codestral"
  export LLM_MODEL="codestral-latest"
  ```
- **Advantages**: No local setup, fast, reliable
- **Best for**: Quick start, production use

### 2. Ollama - **Local**

- **Type**: Local models (runs on your machine)
- **Setup**: Install [Ollama](https://ollama.ai/) and download a model
- **Configuration**:
  ```bash
  export LLM_PROVIDER="ollama"
  export LLM_MODEL="codestral-latest"  # or any model you have
  export OLLAMA_BASE_URL="http://localhost:11434"  # default
  ```
- **Advantages**: Privacy, no API costs, offline use
- **Best for**: Privacy-sensitive data, offline work

### 3. LM Studio - **Local**

- **Type**: Local server (runs on your machine)
- **Setup**: Install [LM Studio](https://lmstudio.ai/) and start a local server
- **Configuration**:
  ```bash
  export LLM_PROVIDER="lmstudio"
  export LLM_MODEL="codestral-latest"  # or any model you loaded
  export LMSTUDIO_BASE_URL="http://localhost:1234"  # default
  ```
- **Advantages**: Privacy, model flexibility, no API costs
- **Best for**: Experimenting with different models, privacy

> **Note**: You can switch providers at runtime via the Settings page in the UI.

---

## 📦 Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional, for secure sandbox execution)
- PostgreSQL (optional, for persistent storage)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Open_Pandas_AI.git
   cd Open_Pandas_AI
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your LLM provider** (choose one):

   **Option A: Codestral (Free API)** - Recommended for beginners
   ```bash
   export MISTRAL_API_KEY="your-api-key-here"
   export LLM_PROVIDER="codestral"
   export LLM_MODEL="codestral-latest"
   ```

   **Option B: Ollama (Local)**
   ```bash
   # Install Ollama first: https://ollama.ai/
   ollama pull codestral-latest
   export LLM_PROVIDER="ollama"
   export LLM_MODEL="codestral-latest"
   export OLLAMA_BASE_URL="http://localhost:11434"
   ```

   **Option C: LM Studio (Local)**
   ```bash
   # Install LM Studio first: https://lmstudio.ai/
   # Start local server in LM Studio
   export LLM_PROVIDER="lmstudio"
   export LLM_MODEL="codestral-latest"
   export LMSTUDIO_BASE_URL="http://localhost:1234"
   ```

4. **Launch the Streamlit interface**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**: Navigate to `http://localhost:8501`

6. **Upload a CSV/Excel file** and ask questions in natural language!

---

## 🏗️ Architecture

The project follows a modular layered architecture:

```
┌─────────────────────────────────────────┐
│         User Interface                   │
│         (Streamlit Pages)                │
├─────────────────────────────────────────┤
│         UI Components                   │
│         (components/)                   │
├─────────────────────────────────────────┤
│         Business Logic                  │
│         (core/)                         │
├─────────────────────────────────────────┤
│         Database                        │
│         (db/)                           │
└─────────────────────────────────────────┘
```

**Key Components**:
- **Session Manager**: Centralized state management across pages
- **LLM Integration**: Multi-provider support (Codestral/Ollama/LM Studio)
- **Intention Detector**: 16 analytical intentions detection
- **Prompt Builder**: Multi-level prompt enrichment
- **Secure Executor**: Docker or subprocess execution with security validation
- **Data Dictionary Manager**: Hybrid dictionary system (auto-detect + manual)
- **Conversational Memory**: Context preservation across exchanges

For detailed architecture documentation, see [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md#-general-architecture).

---

## 🔒 Security

### Multi-Level Security Architecture

1. **AST Validation**: Static code analysis before execution blocks dangerous operations
2. **Execution Isolation**: 
   - **Docker mode** (recommended): Ephemeral containers with complete isolation
   - **Subprocess mode**: Isolated process execution
3. **Resource Limits**: Memory (512MB), CPU (50%), timeout (30s)
4. **Environment Cleanup**: API secrets removed from execution environment
5. **Non-Privileged Execution**: Code runs under restricted user permissions

### Security Flow

```
User Question
    ↓
AI Generated Code
    ↓
AST Validation (code_security.py)
    ├── Blocks imports
    ├── Blocks dangerous functions
    └── Blocks introspection
    ↓
Ephemeral Docker Container (if enabled)
    ├── Network isolation (network_mode=none)
    ├── Resource limits (512MB RAM, 50% CPU)
    ├── Non-privileged user
    └── Auto-destruction after execution
    ↓
Secure Result
```

### Enable Docker Sandbox (Recommended)

1. **Build the sandbox image**:
   ```bash
   chmod +x scripts/build-sandbox.sh
   ./scripts/build-sandbox.sh
   ```

2. **Enable Docker mode**:
   ```bash
   export USE_DOCKER_SANDBOX=true
   export SANDBOX_TIMEOUT_SECONDS=30
   ```

3. **Fallback**: If Docker is unavailable, the system automatically uses subprocess mode.

For more security details, see [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md#-security).

---

## 💡 Usage Examples

### Basic Usage

1. **Load your data**: Upload a CSV or Excel file on the Home page
2. **Ask a question**: Go to the Agent page and type:
   ```
   What are the 5 countries with the most sales?
   ```
3. **Get results**: The AI generates Python/Pandas code, executes it securely, and displays formatted results
4. **Follow up**: Ask related questions - the system maintains context
5. **Export**: Download results as Excel files with professional formatting

### Example Questions

- "Show me the top 10 products by revenue"
- "What is the average age by department?"
- "Create a pivot table of sales by region and product"
- "Find all orders with missing customer information"
- "Calculate the correlation between price and sales"

---

## ⚙️ Configuration

### Environment Variables

**Required**:
- `MISTRAL_API_KEY`: Your Codestral API key (if using Codestral)

**Optional**:
- `LLM_PROVIDER`: `codestral` | `ollama` | `lmstudio` (default: `lmstudio`)
- `LLM_MODEL`: Model name (default: `codestral-latest`)
- `USE_DOCKER_SANDBOX`: Enable Docker sandbox (`true` | `false`, default: `false`)
- `SANDBOX_TIMEOUT_SECONDS`: Execution timeout (default: `30`)
- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://localhost:11434`)
- `LMSTUDIO_BASE_URL`: LM Studio server URL (default: `http://localhost:1234`)
- `DATABASE_URL`: PostgreSQL connection string (for persistent storage)
- `OFFLINE_ONLY`: Set to `true` to hide cloud providers (Codestral) from the UI — enforces 100% local mode

### UI Settings

Access via the Settings page:
- LLM provider selection
- User level (beginner/expert)
- Language (French/English)
- Theme (light/dark)
- Code display toggle
- Display row limits

---

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Tests cover:
- Data validation (`test_data_validator.py`)
- Excel integration (`test_excel_integration.py`)
- Frontend components (`test_frontend_components.py`)
- Complete pipeline (`test_pipeline.py`)
- Utilities (`test_utils.py`)

---

## 🐳 Docker Compose Deployment

For a complete setup with PostgreSQL database:

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Configure your `.env` file**:
   ```env
   MISTRAL_API_KEY=your-api-key-here
   LLM_PROVIDER=codestral
   LLM_MODEL=codestral-latest
   USE_DOCKER_SANDBOX=true
   SANDBOX_TIMEOUT_SECONDS=30
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/openpanda
   ```

3. **Launch everything**:
   ```bash
   docker compose up --build
   ```

4. **Access the application**: `http://localhost:8501`

5. **Database**: PostgreSQL available at `localhost:5432` (default credentials in docker-compose.yml)

---

## 📊 Features in Detail

### 16 Analytical Intentions Detected

The system automatically detects and optimizes for:
1. **Filtering** - Data filtering operations
2. **Sorting** - Sorting and ranking
3. **Statistical** - Statistical calculations
4. **Aggregation** - Groupby, sum, count operations
5. **Time Series** - Temporal analysis
6. **Join** - Data merging
7. **Anomaly Detection** - Outlier identification
8. **Transformation** - Column transformations
9. **Duplicate Handling** - Duplicate management
10. **Missing Values** - Null value handling
11. **Segmentation** - Data segmentation
12. **Ranking** - Ranking and scoring
13. **Comparison** - Data comparisons
14. **Pivot Table** - Pivot table creation
15. **Pattern Detection** - Pattern identification
16. **Export** - Data export operations

### Hybrid Data Dictionary System

- **Automatic Detection**: Recognizes 12+ business domains (E-commerce, CRM, HR, Finance, etc.)
- **Auto-Generation**: Creates dictionary from data if no match found
- **Manual Enrichment**: UI for adding descriptions, business rules, validation rules
- **Impact**: Improves LLM response quality by 15-25%

### Business Agents

Open Pandas-AI includes a **domain-aware agents system** that customizes the LLM prompt based on your data type.

**Available agents**:
| Domain | Agent | Typical tasks |
|--------|-------|---------------|
| Finance | FinanceAgent | Transaction analysis, reporting, reconciliation |
| E-commerce | EcommerceAgent | Sales analysis, AOV, customer segmentation |
| HR | HRAgent | Employee analysis, tenure, salary benchmarks |
| CRM | CRMAgent | Pipeline analysis, lead scoring, conversion |
| Generic | GenericAgent | Default fallback for any dataset |

**Features**:
- **Auto-detection**: The system detects your data domain via column signatures, synonyms (FR/EN), and value types (currency, date, quantity).
- **Manual override**: You can select an agent manually via the dropdown in the Agent page.
- **Follow-up suggestions**: Each agent proposes domain-specific follow-up questions.
- **100% local**: Works offline with LM Studio or Ollama; cloud providers remain optional.

**Extending agents**:

To add a new agent:
1. Create a file `agents/domains/your_domain.py` implementing `BaseAgent` (see `agents/base.py`).
2. Register it in `agents/registry.py`:
   ```python
   from agents.domains.your_domain import YourAgent
   register_agent(YourAgent)
   ```

That's it! The new agent will appear in the selector and will be auto-detected when its signature columns are present.

### Conversational Memory

- Maintains context across questions
- Stores exchange history with metadata
- Generates optimized context for LLM prompts
- Extracts topics for suggestions

---

## 📈 Performance

**Typical processing times**:
- Code generation: 2-5s (depending on provider)
- Code execution: <1s (average data)
- Validation: <0.5s
- **Total**: 3-7s per question

**Recommended limits**:
- DataFrame size: <1M rows (for optimal performance)
- Timeout: 30s (configurable)
- Memory: 512 MB per execution

---

## ⚠️ Current Limitations

- **Single DataFrame**: One DataFrame at a time (no automatic multi-file joins)
- **Manual Error Correction**: Errors require manual retry (auto-correction in development)
- **Limited Visualizations**: No automatic graph generation (coming soon)
- **Data Size**: Optimized for datasets <1M rows
- **Languages**: Primarily French/English support

---

## 🔮 Roadmap

- [ ] Multi-DataFrame support with automatic joins
- [ ] Advanced auto-correction for errors
- [ ] Automatic visualization generation
- [ ] Result caching for performance
- [ ] Additional export formats (JSON, Parquet)
- [ ] Session collaboration/sharing
- [ ] REST API for programmatic access
- [ ] Plugin system for extensions

---

## 🛠️ Technologies

**Backend**:
- Python 3.11
- Streamlit 1.45.1
- Pandas 2.2.3
- SQLAlchemy 2.0.41
- Docker 7.0.0

**LLM Integration**:
- Codestral (Mistral AI) - Free API
- Ollama - Local models
- LM Studio - Local server

**Security**:
- AST analysis
- Docker isolation
- psutil for resource monitoring

**UI/UX**:
- Streamlit Components
- Altair 5.5.0
- Matplotlib 3.10.3

---

## 📚 Documentation

- **[Technical Report](TECHNICAL_REPORT.md)**: Detailed technical documentation
- **[Architecture](TECHNICAL_REPORT.md#-general-architecture)**: System architecture overview
- **[Security](TECHNICAL_REPORT.md#-security)**: Security implementation details
- **[Components](TECHNICAL_REPORT.md#-key-components)**: Key component documentation

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** if applicable
5. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/Open_Pandas_AI.git
cd Open_Pandas_AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8

# Run tests
pytest

# Run code formatter
black .
```

### Code Style

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to functions and classes
- Write tests for new features

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

Developed with ❤️ for AI and data enthusiasts.

**Powered by**:
- [Mistral AI](https://mistral.ai/) - Codestral (free API)
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [LM Studio](https://lmstudio.ai/) - Local LLM server
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Streamlit](https://streamlit.io/) - Web framework

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Open_Pandas_AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Open_Pandas_AI/discussions)
- **Email**: [Your Email]

---

<div align="center">

**Version**: 2.0  
**Last Updated**: 2025

Made with ❤️ by the Open Pandas-AI team

</div>
