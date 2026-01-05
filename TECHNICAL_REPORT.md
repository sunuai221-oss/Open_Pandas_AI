# 📊 Technical Report - Open Pandas-AI

<div align="center">

**Comprehensive Technical Documentation**

[![Version](https://img.shields.io/badge/Version-2.0-blue.svg)](README.md)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-red.svg)](https://streamlit.io/)

[Back to README](README.md) • [Architecture](#-general-architecture) • [Components](#-key-components) • [Security](#-security)

</div>

---

## 📑 Table of Contents

- [Overview](#overview)
- [General Architecture](#-general-architecture)
- [Main Data Flow](#-main-data-flow)
- [Key Components](#-key-components)
- [Database](#-database)
- [User Interface](#-user-interface)
- [Security](#-security)
- [Deployment](#-deployment)
- [Metrics and Performance](#-metrics-and-performance)
- [Testing](#-testing)
- [Technologies Used](#-technologies-used)
- [Strengths](#-strengths)
- [Current Limitations](#-current-limitations)
- [Possible Evolutions](#-possible-evolutions)
- [Conclusion](#-conclusion)

---

## Overview

**Open Pandas-AI** is an intelligent web application for data analysis that allows users to query their CSV/Excel files in natural language and get automatic answers through AI-generated Python/Pandas code.

**Analyzed Version**: 2.0  
**Analysis Date**: 2025  
**Main Framework**: Streamlit (Python)

---

## 🏗️ General Architecture

### Layered Architecture

The project follows a modular multi-layer architecture:

```
┌─────────────────────────────────────────┐
│         User Interface                   │
│         (Streamlit Pages)               │
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

### Directory Structure

```
Open_Pandas_AI/
├── app.py                    # Main entry point
├── pages/                    # Streamlit multi-page pages
│   ├── 1_🏠_Home.py         # Home page (file upload)
│   ├── 2_📊_Data_Explorer.py # Data explorer
│   ├── 3_🤖_Agent.py        # Main AI Agent interface
│   ├── 4_📚_History.py      # Question history
│   ├── 5_⚙️_Settings.py     # Settings
│   └── 6_📈_Dashboard.py   # Dashboard
├── components/               # Reusable UI components
│   ├── chat_interface.py    # Chat interface
│   ├── sidebar.py           # Sidebar
│   ├── result_display.py    # Result display
│   ├── memory_viewer.py     # Memory visualization
│   └── ...
├── core/                    # Main business logic
│   ├── llm.py              # LLM integration (Codestral/Ollama/LM Studio)
│   ├── executor.py         # Secure code execution
│   ├── prompt_builder.py   # Prompt construction
│   ├── intention_detector.py # Analytical intention detection
│   ├── memory.py           # Conversational memory management
│   ├── session_manager.py  # Session manager
│   ├── code_security.py    # Code security validation
│   ├── docker_sandbox_executor.py # Secure Docker execution
│   └── ...
├── db/                      # Database
│   ├── models.py           # SQLAlchemy models
│   ├── queries.py          # Advanced queries
│   └── session.py          # DB session management
└── docker/                  # Docker configuration
    └── sandbox.Dockerfile   # Secure sandbox image
```

---

## 🔄 Main Data Flow

### 1. Data Loading

```
User uploads CSV/Excel file
    ↓
pages/1_🏠_Home.py
    ↓
Automatic dataset type detection
    ↓
Load data dictionary (hybrid system)
    ↓
SessionManager.set_dataframe()
    ↓
Storage in st.session_state
```

### 2. Question Processing

```
User question (natural language)
    ↓
pages/3_🤖_Agent.py
    ↓
IntentionDetector.detect_all() → 16 intentions detected
    ↓
build_prompt() → Enriched prompt construction
    ├── DataFrame context
    ├── Data dictionary
    ├── Detected intentions
    ├── Conversational history
    └── Business context
    ↓
call_llm() → Python/Pandas code generation
    ├── Codestral (Mistral AI) - Free API
    ├── Ollama (local)
    └── LM Studio (local)
    ↓
is_code_safe() → AST security validation
    ↓
execute_code() → Secure execution
    ├── Docker mode (recommended)
    └── Subprocess mode (fallback)
    ↓
format_result_with_validation() → Formatting + validation
    ↓
Display result + suggestions
```

---

## 🧠 Key Components

### 1. Session Management (`core/session_manager.py`)

**Role**: Centralizes application state across Streamlit pages.

**Features**:
- Active DataFrame management (`df`, `df_norm`)
- Exchange storage (questions/answers)
- User configuration (level, language, theme)
- LLM parameters (provider, model)
- Session metrics

**Pattern**: Singleton via `get_session_manager()`

**Main session keys**:
- `df`: Main DataFrame
- `df_norm`: Normalized DataFrame for analysis
- `exchanges`: Exchange history
- `llm_provider`: Selected LLM provider
- `business_domain`: Detected business domain

### 2. LLM Integration (`core/llm.py`)

**Multi-provider support**:
- **Codestral** (Mistral AI): Cloud API (free tier available)
- **Ollama**: Local models
- **LM Studio**: Local server

**Features**:
- Automatic code extraction between `<startCode>`/`<endCode>`
- API error handling
- Configuration via environment variables

**Configuration**:
```python
DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "lmstudio")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "codestral-latest")
```

### 3. Intention Detection (`core/intention_detector.py`)

**16 detected analytical intentions**:

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

**Method**: Keyword analysis (French/English) with regex

**Impact**: Generates specialized instructions for LLM prompts

### 4. Prompt Construction (`core/prompt_builder.py`)

**Multi-level enrichment**:

1. **DataFrame Context**:
   - Preview of first 5 rows
   - Column list with types
   - Type analysis with advice
   - Unique values for categorical columns

2. **Data Dictionary**:
   - Column descriptions
   - Business rules
   - Validation rules
   - Value examples

3. **Detected Intentions**:
   - Specialized instructions per intention
   - Code examples for each type

4. **Conversational Context**:
   - Last 3 exchanges history
   - Previous result summaries

5. **Business Context**:
   - Detected domain (E-commerce, CRM, HR, etc.)
   - Selected business example

**Strict rules enforced**:
- ❌ No imports
- ❌ No `pd.` or `pandas.`
- ❌ Do not overwrite `df`
- ✅ Use direct methods (`df.groupby()`, etc.)
- ✅ Store result in `result`

### 5. Secure Execution (`core/executor.py`)

**Two execution modes**:

#### Docker Mode (recommended)
- Ephemeral containers (auto-destruction)
- Complete network isolation (`network_mode='none'`)
- Resource limits:
  - Memory: 512 MB
  - CPU: 50% quota
- Non-privileged user (`user='sandbox'`)
- Configurable timeout (30s default)

#### Subprocess Mode (fallback)
- Execution in isolated subprocess
- Memory/CPU monitoring (if `psutil` available)
- Reduced CPU priority
- Environment cleanup (API secrets removal)
- Configurable timeout

**Enhanced security**:
- AST validation before execution (`code_security.py`)
- Dangerous imports blocking
- System functions blocking (`open`, `exec`, `eval`)
- Introspection blocking (`__class__`, `__dict__`)

### 6. Security Validation (`core/code_security.py`)

**Static AST analysis**:

**Blocked nodes**:
- `ast.Import`, `ast.ImportFrom`
- `ast.Global`
- `ast.With`, `ast.AsyncWith`

**Blocked functions**:
- `open`, `exec`, `eval`, `compile`
- `os`, `sys`, `subprocess`, `shutil`
- `socket`, `requests`
- `__import__`, `exit`, `quit`

**Blocked attributes**:
- `__class__`, `__dict__`, `__getattribute__`
- `__globals__`, `__mro__`, `__subclasses__`

### 7. Conversational Memory (`core/memory.py`)

**`SessionMemory` class**:

**Features**:
- User/assistant exchange storage with timestamps
- Enriched metadata per message:
  - Analyzed file name
  - Result summary
  - Question ID in DB
- JSON export/import
- Context generation for LLM prompts
- Main topic extraction

**Main methods**:
- `append()`: Add message with metadata
- `get_context_for_prompt()`: Optimized context for LLM
- `get_topics()`: Keyword extraction for suggestions
- `export()` / `import_history()`: Persistence

### 8. Data Dictionary (`core/data_dictionary_manager.py`)

**Hybrid system**:

1. **Automatic detection**:
   - 12+ predefined domains (E-commerce, CRM, HR, Finance, etc.)
   - Column and pattern matching
   - Confidence score

2. **Automatic generation**:
   - If no dictionary found
   - Statistical column analysis
   - Type and description inference

3. **Manual enrichment**:
   - UI interface for completion
   - Add descriptions, business rules
   - Validation rules

**Dictionary structure**:
```python
{
    'dataset_name': str,
    'domain': str,
    'columns': {
        'col_name': {
            'description': str,
            'data_type': str,
            'business_rules': List[str],
            'validation_rules': List[str],
            'examples': List[Any],
            'statistics': Dict
        }
    }
}
```

**Impact**: LLM response quality improvement (+15-25% estimated)

### 9. Error Handling (`core/error_handler.py`)

**Intelligent auto-correction**:

**Process**:
1. Error detection at execution
2. Correction prompt generation with:
   - Original code
   - Error message
   - DataFrame context
3. Retry up to `max_retries` times (default: 2)
4. Security validation at each attempt

**Pattern**: Generator to iterate over corrections

### 10. Formatting and Validation (`core/formatter.py`)

**Enriched validation** (`ResultValidator`):

**Checks**:
- Result/question consistency
- Expected data types
- DataFrame dimensions
- Outlier values
- Data completeness

**Enrichment**:
- Quality score (0-100)
- Contextual warnings
- Automatic interpretation
- Follow-up question suggestions
- Statistical context

---

## 🗄️ Database

### Data Model (`db/models.py`)

**Main tables**:

1. **User**:
   - `id`, `username`, `session_id`
   - `created_at`, `updated_at`

2. **UploadedFile**:
   - `id`, `filename`, `preview`, `checksum`
   - `uploaded_at`, `user_id`

3. **Question**:
   - `id`, `question` (text)
   - `created_at`, `user_id`, `file_id`

4. **CodeExecution**:
   - `id`, `code`, `result`, `status`
   - `error_message`, `execution_time`
   - `model_used`, `question_id`

5. **ConsultingMessage**:
   - `id`, `message`, `role`
   - `model_used`, `question_id`

**Relations**:
- User → UploadedFile (1-N)
- User → Question (1-N)
- Question → CodeExecution (1-N)
- Question → ConsultingMessage (1-N)
- UploadedFile → Question (1-N)

### Advanced Queries (`db/queries.py`)

**Features**:
- Question search by text
- Session statistics
- Execution history
- Success rate
- Popular topics
- Daily statistics

---

## 🎨 User Interface

### Streamlit Pages

#### 1. Home (`pages/1_🏠_Home.py`)
- **Role**: File upload and management
- **Features**:
  - CSV/Excel upload (multi-file)
  - Automatic dictionary detection
  - Data preview
  - Quick actions (Explore, Analyze, Export)

#### 2. Data Explorer (`pages/2_📊_Data_Explorer.py`)
- **Role**: Data quality exploration
- **Features**:
  - Quality metrics
  - Anomaly detection
  - Statistical visualizations
  - Data validation

#### 3. Agent (`pages/3_🤖_Agent.py`)
- **Role**: Main conversational interface
- **Features**:
  - Chat interface
  - Real-time code generation
  - Enriched result display
  - Follow-up suggestions
  - Automatic visualizations
  - Excel export

#### 4. History (`pages/4_📚_History.py`)
- **Role**: Question history
- **Features**:
  - Question/answer list
  - Search
  - Re-execution
  - History export

#### 5. Settings (`pages/5_⚙️_Settings.py`)
- **Role**: Configuration
- **Features**:
  - LLM provider selection
  - User level
  - Language
  - Theme
  - Code display

#### 6. Dashboard (`pages/6_📈_Dashboard.py`)
- **Role**: Statistics dashboard
- **Features**:
  - Session metrics
  - Usage charts
  - Top questions
  - Performance

### UI Components (`components/`)

**Main components**:
- `chat_interface.py`: Chat messages
- `result_display.py`: Formatted result display
- `memory_viewer.py`: Memory visualization
- `suggestions.py`: Question suggestions
- `sidebar.py`: Navigation sidebar
- `skills_catalog.py`: Agent capabilities catalog
- `theme_manager.py`: Theme management

---

## 🔒 Security

### Multi-level Security

1. **Static AST validation**:
   - Analysis before execution
   - Dangerous pattern blocking

2. **Execution isolation**:
   - Docker: complete isolation
   - Subprocess: process isolation

3. **Resource limits**:
   - Memory: 512 MB max
   - CPU: 50% quota
   - Timeout: 30s default

4. **Environment cleanup**:
   - API secrets removal
   - Proxy disabling
   - Cleaned environment variables

5. **Non-privileged user**:
   - Execution under `sandbox` user
   - No network access (Docker mode)

---

## 🚀 Deployment

### Docker Compose

**Services**:
1. **app**: Streamlit application
   - Port: 8501
   - Environment variables: `.env`
   - Docker socket volume for sandbox

2. **db**: PostgreSQL
   - Port: 5432
   - Database: `openpanda`
   - Healthcheck configured

**Configuration**:
```yaml
USE_DOCKER_SANDBOX: "true"
SANDBOX_TIMEOUT_SECONDS: "30"
DATABASE_URL: postgresql+psycopg2://...
```

### Environment Variables

**Required**:
- `MISTRAL_API_KEY`: Codestral API key (if using Codestral)

**Optional**:
- `LLM_PROVIDER`: LLM provider (codestral/ollama/lmstudio)
- `LLM_MODEL`: Model to use
- `USE_DOCKER_SANDBOX`: Enable Docker sandbox
- `SANDBOX_TIMEOUT_SECONDS`: Execution timeout
- `OLLAMA_BASE_URL`: Ollama URL
- `LMSTUDIO_BASE_URL`: LM Studio URL

---

## 📊 Metrics and Performance

### Response Quality

**Phase 2 Improvements**:
- Intention detection: +15-25% estimated quality
- Enriched dictionary: Better context understanding
- Result validation: Automatic error detection

### Performance

**Typical processing time**:
- Code generation: 2-5s (depending on provider)
- Code execution: <1s (average data)
- Validation: <0.5s
- Total: 3-7s per question

**Limits**:
- Timeout: 30s (configurable)
- Memory: 512 MB per execution
- DataFrame size: Recommended <1M rows

---

## 🧪 Testing

### Test Structure (`tests/`)

**Available tests**:
- `test_data_validator.py`: Data validation
- `test_excel_integration.py`: Excel integration
- `test_excel_utils.py`: Excel utilities
- `test_frontend_components.py`: UI components
- `test_pipeline.py`: Complete pipeline
- `test_utils.py`: General utilities

**Execution**:
```bash
pytest
```

---

## 🔧 Technologies Used

### Backend
- **Python 3.11**
- **Streamlit 1.45.1**: Web framework
- **Pandas 2.2.3**: Data manipulation
- **SQLAlchemy 2.0.41**: Database ORM
- **Docker 7.0.0**: Containerization
- **psycopg2 2.9.10**: PostgreSQL driver

### LLM Integration
- **Codestral (Mistral AI)**: Cloud API (free tier)
- **Ollama**: Local models
- **LM Studio**: Local server

### Security
- **AST**: Syntax analysis
- **Docker**: Container isolation
- **psutil**: Resource monitoring

### UI/UX
- **Streamlit Components**: Native components
- **Altair 5.5.0**: Visualizations
- **Matplotlib 3.10.3**: Charts

---

## 📈 Strengths

1. **Modular architecture**: Clear separation of responsibilities
2. **Enhanced security**: Multi-level protection
3. **Multi-provider LLM**: Model choice flexibility
4. **Intelligent detection**: Intentions + automatic dictionaries
5. **Enriched validation**: Guaranteed result quality
6. **Conversational memory**: Preserved context
7. **Intuitive interface**: Streamlit multi-pages
8. **Extensibility**: Easy to add providers/features

---

## ⚠️ Current Limitations

1. **Single DataFrame at a time**: No automatic multi-file joins
2. **No automatic correction**: Errors require manual retry
3. **Limited visualizations**: No automatic graph generation
4. **Data size**: Optimized for datasets <1M rows
5. **Languages**: Mainly French/English

---

## 🔮 Possible Evolutions

1. **Multi-DataFrames**: Automatic join support
2. **Advanced auto-correction**: Automatic error correction
3. **Automatic visualizations**: Intelligent graph generation
4. **Result caching**: Performance optimization
5. **Export formats**: JSON, Parquet, etc.
6. **Collaboration**: Session sharing between users
7. **REST API**: Programmatic access
8. **Plugins**: Extension system

---

## 📝 Conclusion

**Open Pandas-AI** is a mature and well-architected application for AI-assisted data analysis. The modular architecture, enhanced security, and advanced features (intention detection, enriched dictionaries) make it a powerful tool for natural language data analysis.

The project demonstrates a good understanding of security challenges in executing AI-generated code, with multiple levels of protection (AST, Docker, resource limits).

Recent improvements (Phase 2) with the hybrid dictionary system and intention detection show continuous evolution towards better response quality.

---

<div align="center">

**Report generated on**: 2025  
**Analyzed project version**: 2.0  
**Analysis author**: AI Assistant

[Back to README](README.md)

</div>
