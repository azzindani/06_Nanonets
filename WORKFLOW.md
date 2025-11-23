# Development Workflow

This document describes the AI-assisted development workflow used to build and maintain this project. **Use this as a prompt template for future projects.**

## Overview

This project uses Claude Code as an AI development assistant to:
- Implement features and refactor code
- Write and fix tests
- Manage Git operations
- Ensure CI/CD compliance
- Maintain code quality and alignment

---

## Project Definition Methodology

When starting a new project, follow this structured approach:

### 1. Define Architecture First

Before writing code, establish the system architecture:

```markdown
## System Architecture Template

### Core Components
1. **Data Layer** - How data flows in/out
2. **Processing Layer** - Business logic
3. **Interface Layer** - User interaction points
4. **Infrastructure** - Models, configs, utilities

### Data Flow
Query → Detection → Processing → Generation → Response

### Component Relationships
- Define which components depend on others
- Identify shared resources (models, configs)
- Plan for lazy loading to avoid import issues
```

### 2. Define Feature Roadmap

Organize features by deployment priority:

```markdown
## Feature Prioritization

### Minimum Viable Product (MVP)
Required for first deployment:
- [ ] Core functionality (search, retrieval)
- [ ] Basic API endpoint
- [ ] Configuration management
- [ ] Error handling and logging

### Phase 1: Production Ready
- [ ] Complete test coverage
- [ ] CI/CD pipeline
- [ ] Docker deployment
- [ ] Documentation

### Phase 2: Enhanced Features
- [ ] User interface (Gradio/Streamlit)
- [ ] Multiple providers
- [ ] Caching and optimization
- [ ] Analytics

### Phase 3: Advanced
- [ ] Multi-database support
- [ ] Advanced analytics
- [ ] Collaborative features
```

### 3. Define Directory Structure

Plan the codebase organization:

```markdown
## Directory Structure Guidelines

### Root Level
- config.py          # All settings in one place
- main.py            # Single entry point
- requirements.txt   # Dependencies
- Dockerfile         # Deployment

### Module Organization
project/
├── core/            # Business logic
│   ├── search/      # Retrieval components
│   └── generation/  # Output components
├── providers/       # External integrations
├── pipeline/        # High-level orchestration
├── api/             # REST endpoints
├── ui/              # User interfaces
└── tests/           # Test infrastructure

### Naming Conventions
- Modules: lowercase_with_underscores
- Classes: PascalCase
- Functions: lowercase_with_underscores
- Constants: UPPERCASE_WITH_UNDERSCORES
```

### 4. Define Minimum Deployment Requirements

```markdown
## Deployment Checklist

### Must Have
- [ ] All unit tests passing
- [ ] No import errors in CI
- [ ] Environment variable documentation
- [ ] Health check endpoint
- [ ] Graceful error handling

### Should Have
- [ ] Docker support
- [ ] CI/CD pipeline
- [ ] API documentation
- [ ] Performance benchmarks

### Nice to Have
- [ ] Kubernetes configs
- [ ] Monitoring/alerting
- [ ] Auto-scaling
```

---

## Code Organization Patterns

### Lazy Import Pattern

Prevent import errors during CI testing:

```python
# In __init__.py
def __getattr__(name):
    if name == 'HeavyClass':
        from .heavy_module import HeavyClass
        return HeavyClass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['HeavyClass']
```

### Singleton Pattern

For shared resources:

```python
_instance = None

def get_instance():
    global _instance
    if _instance is None:
        _instance = MyClass()
    return _instance
```

### Factory Pattern

For pluggable components:

```python
PROVIDERS = {
    'local': LocalProvider,
    'api': APIProvider,
}

def create_provider(name, config=None):
    return PROVIDERS[name](config)
```

### Runnable Test Blocks

Add to every module for direct testing:

```python
if __name__ == "__main__":
    print("=" * 60)
    print("MODULE TEST")
    print("=" * 60)

    # Test code here
    instance = MyClass()
    result = instance.test_method()
    print(f"  ✓ Test passed: {result}")

    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
```

---

## Hardware and Resource Management

### Multi-GPU Detection

```python
@dataclass
class HardwareConfig:
    embedding_device: str      # 'cpu' or 'cuda:N'
    llm_device: str
    quantization: str          # 'none', '4bit', '8bit'
    device_map: Dict[str, int] # component -> gpu_index

def detect_hardware() -> HardwareConfig:
    # Auto-detect and distribute workloads
    pass
```

### Provider Abstraction

```python
class BaseProvider(ABC):
    @abstractmethod
    def initialize(self) -> bool: pass

    @abstractmethod
    def generate(self, prompt: str) -> str: pass

    @abstractmethod
    def shutdown(self) -> None: pass
```

---

## Testing Strategy

### Test Categories

```python
# Unit tests - no external dependencies
@pytest.mark.unit
def test_query_detection():
    pass

# Integration tests - requires models
@pytest.mark.integration
def test_full_pipeline():
    pass

# Skip if dependency missing
numpy = pytest.importorskip("numpy")
```

### Test File Structure

```
tests/
├── unit/           # Fast, no GPU
├── integration/    # Requires models
└── conftest.py     # Shared fixtures
```

### Running Tests

```bash
# Unit only (CI)
pytest -m unit -v

# Integration (local with GPU)
pytest -m integration -v

# Specific module
python -m module_name  # Uses __main__ block
```

---

## Branch Strategy

### Feature Branches
- All development happens on feature branches: `claude/<feature-name>-<session-id>`
- Never push directly to `main` or `master`
- Each session gets a unique branch for tracking

### Git Operations
```bash
# Always use -u flag when pushing
git push -u origin claude/<branch-name>

# Commit with descriptive messages using HEREDOC
git commit -m "$(cat <<'EOF'
Short summary line

- Detailed change 1
- Detailed change 2
EOF
)"
```

---

## Development Cycle

### 1. Task Planning
- Break complex tasks into smaller, trackable items
- Use todo lists to track progress
- Prioritize based on dependencies

### 2. Implementation
- Follow existing code patterns
- Use lazy imports to avoid heavy dependencies during testing
- Prefer editing existing files over creating new ones

### 3. Testing
- Run tests frequently: `pytest -m unit -v`
- Fix failing tests before committing
- Use `pytest.importorskip()` for optional dependencies
- Mark tests appropriately:
  - `@pytest.mark.unit` - No external dependencies
  - `@pytest.mark.integration` - Requires models/GPU

### 4. CI Compliance
- Ensure all unit tests pass locally before pushing
- Use lazy imports in `__init__.py` files to prevent import errors
- Check that requirements.txt has all dependencies uncommented

### 5. Code Review
- Verify alignment with original code (e.g., Kaggle_Demo.ipynb)
- Check that new features integrate properly
- Ensure backward compatibility

---

## Common Commands

### Testing
```bash
# Run all unit tests
pytest -m unit -v

# Run specific test file
pytest tests/unit/test_providers.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run module directly
python -m core.analytics
python -m providers.factory
python -m conversation.context_cache
python -m hardware_detection
```

### Git
```bash
# Check status
git status

# View recent commits
git log --oneline -5

# Stage and commit
git add -A && git commit -m "message"

# Push to remote
git push -u origin <branch-name>
```

### Development
```bash
# Run Gradio UI
python ui/gradio_app.py

# Run FastAPI server
python api/server.py

# Run CLI
python main.py --query "your question"

# Hardware detection
python hardware_detection.py
```

---

## CI/CD Pipeline

### GitHub Actions Workflow
1. **Test Job** - Runs unit tests on Python 3.9, 3.10, 3.11
2. **Lint Job** - Checks formatting with Black, isort, flake8
3. **Build Job** - Creates distribution package
4. **Docker Job** - Builds and tests Docker image (on main only)

### CI Requirements
- All unit tests must pass
- No critical linting errors (E9, F63, F7, F82)
- Package must build successfully

---

## Troubleshooting

### Import Errors in CI
**Problem**: `ModuleNotFoundError: No module named 'torch'`

**Solution**: Use lazy imports in `__init__.py`:
```python
def __getattr__(name):
    if name == 'HeavyClass':
        from .heavy_module import HeavyClass
        return HeavyClass
    raise AttributeError(...)
```

### Test Failures
**Problem**: Tests fail due to missing dependencies

**Solution**: Add skip markers:
```python
import pytest
numpy = pytest.importorskip("numpy")
```

### API Mismatches
**Problem**: Tests use wrong method names

**Solution**: Check actual implementation and update tests:
```python
# Wrong: detector.detect(query)
# Right: detector.analyze_query(query)
```

---

## Best Practices

### Code Quality
- Follow existing patterns in the codebase
- Add type hints for function signatures
- Include docstrings for public APIs
- Log important operations with `logger_utils`

### Testing
- Test one thing per test function
- Use descriptive test names
- Include both positive and edge cases
- Mock external dependencies

### Documentation
- Update README when adding features
- Document configuration options in .env.example
- Keep directory structure map current

### Git Commits
- Use present tense ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Include details in commit body
- Reference issues when applicable

---

## Session Workflow Example

```
1. User: "Add feature X"

2. Claude: Creates todo list
   - [ ] Research existing code
   - [ ] Implement feature
   - [ ] Write tests
   - [ ] Update documentation

3. Claude: Implements feature, marking todos as complete

4. Claude: Runs tests
   $ pytest -m unit -v

5. Claude: Fixes any failures

6. Claude: Commits and pushes
   $ git add -A
   $ git commit -m "Add feature X"
   $ git push -u origin claude/branch-name

7. User: Reviews and provides feedback

8. Repeat until complete
```

---

## Prompt Template for New Projects

Use this template when starting a new AI-assisted project:

```markdown
# Project: [Name]

## Architecture
[Define high-level architecture with ASCII diagrams]

## Features by Priority

### MVP (Required for deployment)
- [ ] Feature 1
- [ ] Feature 2

### Phase 1 (Production ready)
- [ ] Feature 3
- [ ] Feature 4

### Phase 2 (Enhanced)
- [ ] Feature 5

## Directory Structure
```
project/
├── core/           # Business logic
├── api/            # Endpoints
├── ui/             # Interface
└── tests/          # Testing
```

## Deployment Requirements
- [ ] Unit tests passing
- [ ] Docker support
- [ ] Environment docs

## Conventions
- Use lazy imports for heavy dependencies
- Add __main__ blocks for direct testing
- Follow existing patterns
```

---

## Alignment Verification

When refactoring from monolithic code (like Jupyter notebooks):

1. **List original components**
   ```bash
   grep "^class \|^def " original.py
   ```

2. **Map to modular structure**
   - Original `ClassName` → `module/class_name.py`

3. **Verify functionality**
   - Check method signatures match
   - Ensure return types are compatible
   - Test with same inputs

4. **Document differences**
   - New features not in original
   - Improved implementations
   - Breaking changes

---

## Contributing

1. Create feature branch from main
2. Follow development cycle above
3. Ensure CI passes
4. Submit PR with description
5. Address review feedback
6. Merge when approved

---

## Complete Project Development Workflow

This section documents the actual development workflow used to build Nanonets VL from start to production-ready state. Use this as a comprehensive template for future projects.

### Phase 1: Foundation & Core Engine

**Goal**: Get basic OCR processing working

1. **Project Structure Setup**
   ```bash
   # Create directory structure
   mkdir -p core models api/routes api/middleware api/schemas ui services utils tests/unit tests/integration
   ```

2. **Core Components** (in order)
   - `config.py` - Central configuration with pydantic-settings
   - `models/hardware_detection.py` - GPU/CPU detection
   - `models/model_manager.py` - Model loading with lazy initialization
   - `core/ocr_engine.py` - Main OCR processing
   - `core/document_processor.py` - PDF/image handling

3. **Verification**
   ```bash
   python -m core.ocr_engine  # Should process test image
   ```

### Phase 2: Processing Pipeline

**Goal**: Complete text extraction and structuring

1. **Processing Components**
   - `core/output_parser.py` - HTML/text parsing
   - `core/field_extractor.py` - Field extraction with patterns
   - `core/format_converter.py` - JSON/XML/CSV conversion
   - `utils/logger.py` - Structured logging
   - `utils/validators.py` - Input validation

2. **Testing Strategy**
   ```bash
   # Add self-test blocks to each module
   if __name__ == "__main__":
       print("=" * 60)
       print("MODULE TEST")
       # Test code here
   ```

### Phase 3: API Layer

**Goal**: REST API with authentication

1. **API Components**
   - `api/server.py` - FastAPI application
   - `api/routes/ocr.py` - OCR endpoints
   - `api/routes/health.py` - Health checks
   - `api/middleware/auth.py` - API key authentication
   - `api/middleware/rate_limit.py` - Rate limiting (token bucket + sliding window)
   - `api/schemas/` - Request/response models

2. **API Versioning Pattern**
   ```python
   # v1 - Legacy format
   @router.post("/ocr")
   async def process_document_v1(): pass

   # v2 - Enhanced structured output
   @router.post("/v2/ocr")
   async def process_document_v2(): pass

   # Batch processing
   @router.post("/ocr/batch")
   async def process_batch(): pass
   ```

3. **Verification**
   ```bash
   python main.py --mode api
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/api/v1/ocr -F "file=@test.pdf"
   ```

### Phase 4: Gradio UI

**Goal**: Full web interface

1. **UI Components**
   - `ui/app.py` - Main Gradio application
   - Tabs: Process & Results, API Config, Formats
   - Sample documents integration
   - Dual API v1/v2 viewers

2. **UI Best Practices**
   ```python
   # Custom CSS for styling
   custom_css = """
   .small-upload span { font-size: 9px !important; }
   """

   # Sample documents
   gr.Examples(
       examples=[[path] for path in sample_files],
       inputs=[file_input]
   )
   ```

### Phase 5: AI-Native Features

**Goal**: Document intelligence capabilities

1. **Document Classification** (`core/document_classifier.py`)
   ```python
   # Pattern-based classification
   DocumentType = Enum('DocumentType', [
       'INVOICE', 'RECEIPT', 'CONTRACT', 'FORM',
       'BANK_STATEMENT', 'ID_DOCUMENT', 'MEDICAL', 'TAX_DOCUMENT'
   ])
   ```

2. **Language Detection** (`core/language_support.py`)
   ```python
   # Multi-language support with script detection
   - 50+ language codes
   - Script detection (Latin, CJK, Arabic, Cyrillic)
   - Confidence scoring
   ```

3. **Entity Extraction** (`core/semantic_extractor.py`)
   ```python
   # Entity types with false positive filtering
   entity_types = ['person', 'money', 'date', 'email', 'phone', 'organization', 'address']

   # Exclusion patterns for common false positives
   _person_exclusions = {'bill to', 'ship to', 'sold to', ...}
   ```

4. **Structured Output** (`core/structured_output.py`)
   ```python
   # Document-type-specific extraction patterns
   DOCUMENT_PATTERNS = {
       DocumentType.INVOICE: {
           'invoice_number': [r'Invoice\s*#?\s*:?\s*([A-Z0-9\-]+)'],
           'date': [...],
           'total': [...],
       },
       DocumentType.BANK_STATEMENT: {...},
       DocumentType.ID_DOCUMENT: {...},
   }
   ```

### Phase 6: Production Readiness

**Goal**: 100% test success, load testing, documentation

1. **Testing Hierarchy**
   ```
   tests/
   ├── unit/                    # Fast, no dependencies
   │   ├── test_document_classifier.py
   │   ├── test_language_support.py
   │   ├── test_semantic_extractor.py
   │   └── test_structured_output.py
   ├── integration/             # API and pipeline tests
   │   ├── test_api_v2.py
   │   └── test_full_pipeline.py
   ├── performance/             # Load testing
   │   ├── benchmark.py
   │   └── locustfile.py
   └── asset/                   # Sample documents
       ├── invoice1-9.pdf
       └── docparsing_example*.jpg
   ```

2. **Load Testing with Locust**
   ```python
   # locustfile.py
   class OCRUser(HttpUser):
       @task(3)
       def process_document(self):
           with open('test.pdf', 'rb') as f:
               self.client.post('/api/v1/ocr', files={'file': f})

       @task(1)
       def health_check(self):
           self.client.get('/api/v1/health')
   ```

3. **Run Load Tests**
   ```bash
   # Start server
   python main.py --mode api

   # Run load test (separate terminal)
   locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 60s
   ```

4. **Success Criteria**
   - ✅ 100% success rate (no 4xx/5xx errors)
   - ✅ Response time p95 < 5s
   - ✅ Throughput > 100 req/s (health checks)
   - ✅ All test categories passing

### Phase 7: Documentation & Alignment

**Goal**: Comprehensive documentation aligned with code

1. **Documentation Files**
   - `README.md` - Project overview, features, directory structure
   - `DOCUMENTATION.md` - API reference, usage examples
   - `FUTURE_ROADMAP.md` - Future features, improvements
   - `WORKFLOW.md` - Development methodology (this file)

2. **Alignment Process**
   ```bash
   # List actual files
   find . -name "*.py" | grep -v __pycache__ | sort

   # Compare with documented structure
   # Update checkboxes for completed features
   # Mark completed sprints/phases
   ```

3. **Checklist Pattern**
   ```markdown
   ### Sprint 1: Foundation ✅
   - [x] Set up project structure
   - [x] Implement config.py
   - [x] Port core/ocr_engine.py

   **Milestone**: `python -m core.ocr_engine` works ✅
   ```

---

## Complete Test Command Suite

Use this comprehensive test suite for any project:

```python
# ============================================
# CELL 1: SETUP
# ============================================
!pip install -q gradio fastapi uvicorn locust pytest pytest-cov httpx

# ============================================
# CELL 2: SYNTAX CHECK
# ============================================
!python -m py_compile config.py core/*.py api/*.py services/*.py ui/*.py

# ============================================
# CELL 3: MODULE SELF-TESTS
# ============================================
!python -m core.test_complete_ocr
!python -m services.test_services
!python -m api.test_api

# ============================================
# CELL 4: UNIT TESTS
# ============================================
!pytest tests/unit/ -v --tb=short

# ============================================
# CELL 5: INTEGRATION TESTS
# ============================================
!pytest tests/integration/ -v --tb=short

# ============================================
# CELL 6: COVERAGE REPORT
# ============================================
!pytest tests/ -v --cov=core --cov=api --cov-report=term-missing

# ============================================
# CELL 7: API ENDPOINT TESTS
# ============================================
import subprocess
import time

server = subprocess.Popen(['python', 'main.py', '--mode', 'api'])
time.sleep(30)

!curl -s http://localhost:8000/health
!curl -s -X POST http://localhost:8000/api/v1/ocr -F "file=@tests/asset/invoice1.pdf"
!curl -s -X POST http://localhost:8000/api/v1/v2/ocr -F "file=@tests/asset/invoice1.pdf"
!curl -s -X POST http://localhost:8000/api/v1/ocr/batch -F "files=@tests/asset/invoice1.pdf" -F "files=@tests/asset/invoice2.pdf"

server.terminate()

# ============================================
# CELL 8: LOAD TEST
# ============================================
server = subprocess.Popen(['python', 'main.py', '--mode', 'api'])
time.sleep(30)

!locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 60s

server.terminate()

# ============================================
# CELL 9: CONCURRENT TEST
# ============================================
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)
start = time.time()
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda _: client.get("/api/v1/health").status_code, range(100)))
elapsed = time.time() - start

print(f"Success: {results.count(200)}/100")
print(f"Throughput: {100/elapsed:.1f} req/s")
```

---

## Project Completion Checklist

Use this checklist before marking a project as production-ready:

### Core Functionality
- [ ] All core modules have self-test blocks
- [ ] Hardware detection works (GPU/CPU)
- [ ] Model loading with quantization
- [ ] End-to-end processing pipeline

### API Layer
- [ ] Health check endpoint
- [ ] Main processing endpoint
- [ ] API versioning (v1/v2)
- [ ] Batch processing
- [ ] Rate limiting
- [ ] Authentication

### Testing
- [ ] Unit tests for all modules
- [ ] Integration tests for API
- [ ] Performance benchmarks
- [ ] Load tests with Locust
- [ ] 100% success rate achieved

### Documentation
- [ ] README with features marked as complete
- [ ] API documentation with examples
- [ ] Directory structure matches reality
- [ ] Future roadmap with completed phases marked

### Deployment
- [ ] Docker support
- [ ] Environment variables documented
- [ ] CI/CD pipeline configured
- [ ] Sample documents included

---

## Quick Reference Commands

```bash
# Development
python main.py --mode api          # Start API server
python main.py --mode ui           # Start Gradio UI
UI_SHARE=true python run_ui.py     # Gradio with public URL

# Testing
pytest tests/ -v                   # All tests
pytest tests/unit/ -v              # Unit tests only
pytest --cov=core --cov-report=html # Coverage report
python -m core.test_complete_ocr   # Module self-test

# Load Testing
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Git
git status
git log --oneline -5
git add -A && git commit -m "message"
git push -u origin branch-name

# API Testing
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/ocr -F "file=@test.pdf"
curl -X POST http://localhost:8000/api/v1/v2/ocr -F "file=@test.pdf"
```

---

## Lessons Learned

### What Worked Well
1. **Module self-tests** - Each module having `if __name__ == "__main__"` block for quick testing
2. **Progressive API versioning** - v1 for compatibility, v2 for enhanced features
3. **Entity exclusion lists** - Preventing false positives in extraction
4. **Load testing early** - Finding batch endpoint 405 error before production
5. **Sample documents** - Real test assets from day one

### Common Issues & Solutions
1. **False positive entity detection** → Add exclusion lists
2. **Batch endpoint 405** → Add missing endpoint route
3. **CSS not applying in Gradio** → Use elem_classes with specific selectors
4. **Import errors in CI** → Lazy imports in __init__.py
5. **Documentation drift** → Alignment verification process

### Architecture Decisions
1. **Unified structured output** - Single processor combining classification, extraction, entities
2. **Document-type patterns** - Specialized extraction for each document type
3. **Dual API format** - v1 for simple, v2 for structured
4. **Rate limiting modes** - Token bucket for bursts, sliding window for sustained
