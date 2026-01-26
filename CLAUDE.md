# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Environment Setup
```bash
# Install uv (recommended package manager)
pip install uv

# Install dependencies and create virtual environment
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Running the Application
```bash
# Run Dash web application
python -m dash_web.app

# Access at http://localhost:8050
```

### Data Management
```bash
# Update all financial data from sources
python -m utils.update_datas

# Note: Data is stored in datas/raw/ (source data) and datas/processed/ (cleaned data)
```

### Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Service runs on port 8050
```

### Development Tools
```bash
# Compile requirements from requirements.in
pip-compile requirements.in

# Show dependency tree
pipdeptree
```

## Architecture Overview

This is a **multi-layered quantitative trading platform** that processes financial data, implements investment strategies, and presents analysis through a web interface.

### Data Flow Architecture

```
Data Sources → Data Collection → Raw Storage → Processing → Processed Storage → Web Pages → Visualization
     ↓              ↓                ↓             ↓                ↓              ↓           ↓
  akshare,    update_datas.py    datas/raw/   clean_data.py   datas/processed/ dash_web/   Plotly
  efinance,                                          & logic modules
  yfinance
```

### Layer Structure

**1. Data Collection Layer** (`utils/update_datas.py`)
- Orchestrates data fetching from multiple providers (akshare, efinance, yfinance, easyquotation)
- Stores raw data in `datas/raw/` organized by asset class
- Each data source function is independent with error handling and logging

**2. Data Processing Layer** (`utils/clean_data.py`, `utils/logics/`)
- Cleans and normalizes raw data
- Merges data from multiple sources
- Implements investment strategies as standalone logic modules

**3. Strategy Layer** (`utils/logics/`)
- `index_logic.py`: Index fund strategies (valuation, trend-following, rotation)
- `bond_logic.py`: Bond analysis strategies
- Each strategy module defines enums for strategy types and dataclasses for metrics

**4. Presentation Layer** (`dash_web/`)
- Multi-page Dash application with Bootstrap theming
- Each page in `dash_web/pages/` is self-contained with its own imports
- Uses Plotly for interactive charts
- Theme switching supported via dropdown (20+ Bootstrap themes)

### Key Directories

```
dash_web/pages/          # Individual dashboard pages (home, index, bond, reits, etc.)
utils/logics/            # Investment strategy implementations
utils/                   # Data collection and processing utilities
datas/raw/               # Raw data from providers (organized by asset class)
datas/processed/         # Cleaned and merged data for efficient loading
logs/                    # Loguru log files
```

### Page Registration Pattern

Pages are registered automatically via Dash's page registry. Navigation order is controlled by `CUSTOM_ORDER` in `dash_web/app.py`. When adding a new page:

1. Create file in `dash_web/pages/` with `dash.register_page(__name__)`
2. Add page name to `CUSTOM_ORDER` list in `dash_web/app.py`

### Constants and Mappings

Financial constants and symbol mappings are centralized in `utils/constants.py`. This includes index codes, asset class mappings, and configuration values.

### Data Source Patterns

- **Chinese markets**: akshare, efinance, easyquotation
- **International markets**: yfinance
- **Real-time quotes**: easyquotation for domestic, yfinance for international
- **Macroeconomic data**: akshare and official statistics sources

### Logging Convention

Use `loguru` for all logging. Initialize with `utils.set_log.set_log('filename.log')`. Logs are written to `logs/` directory with timestamps and error tracking.

### Environment Variables

- `DEBUG`: Debug mode toggle
- `JISILU_COOKIES`: Cookies for premium data access (optional)
- Copy `.envExample` to `.env` for local configuration

### Page Development Pattern

Each page follows this structure:
1. Import required libraries (pandas, plotly, dash components)
2. Load data from `datas/processed/`
3. Define layout with dbc.Card components for organization
4. Create Plotly figures with go.Figure
5. Add callbacks for interactivity (optional)

### Adding New Data Sources

1. Add function to `utils/update_datas.py`
2. Save to appropriate `datas/raw/` subdirectory
3. Add processing logic to `utils/clean_data.py` or create new processor
4. Store processed data in `datas/processed/`
5. Reference in dashboard page

### Investment Strategy Implementation

Strategies are implemented as pure functions in `utils/logics/`:
- Accept pandas DataFrames as input
- Return structured results (dataclasses or DataFrames)
- Use enums for strategy types
- Include comprehensive docstrings explaining the algorithm

### Data Processing Strategy: Raw vs Processed

Pages choose between raw and processed data based on performance and complexity:

#### **Use Processed Data** (`datas/processed/`)
When data is large, requires complex computation, or expensive multi-source merging:
- **index.py**: Merged global indices with normalization (multiple sources, heavy computation)
- **reits.py**: Historical merged REITs data (time-series aggregation)
- **period.py**: GDP/CPI macroeconomic data (multi-source merging)

#### **Use Raw Data** (`datas/raw/` or `datas/virtual/`)
When data is small, simple to merge, or requires real-time updates:
- **virtual.py**: Cryptocurrency data (small datasets, simple merge)
- **bond.py**: Convertible bonds (latest data needed, complex business logic in-page)
- **metals.py**: Precious metals prices (real-time quotes)
- **home.py**: News feeds (latest aggregation)

#### **Decision Criteria**
| Factor | Processed | Raw |
|--------|-----------|-----|
| Data size | Large | Small |
| Computation | Complex (normalization, aggregation) | Simple (merge, filter) |
| Update frequency | Stable | Frequent |
| Page load impact | Pre-computed (fast) | Real-time (acceptable if fast) |

#### **Performance Consideration**
Page load time increases when processing large datasets. Pre-process heavy computations into `datas/processed/`, but simple merges (under ~10k rows) are acceptable in-page.
