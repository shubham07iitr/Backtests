# Backtesting System

A Python-based backtesting framework for options trading strategies with comprehensive analytics and PDF reporting.

## Features

- Currently hosts only a single BT for NIFTY options (A simple BTST strategy), more will be added
- Executes BT on historical options data starting from 2022
- Generate equity curves and drawdown analysis
- Calculate key metrics: Sharpe, Sortino, Calmar ratios
- Monthly returns heatmap with color-coded performance
- Professional PDF reports with charts and metrics
- Support for gross, execution, and net returns
- Cross-platform support (Windows/Mac/Linux) 

## Requirements

- Python 3.12+
- Dependencies listed in `requirements.txt`

## Installation
```bash
# Clone the repository
git clone 
cd 

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running a Backtest

Navigate to a specific strategy folder and run:  
```bash
cd strategies/btst_v1_1dec  ← CHANGED (was "runs/btst_v1_1dec")
python3 main.py
```

This will:
- Execute the backtest using the strategy defined in `logic.py`
- Use parameters from `config.py`
- Save results to `results/btst_v1_1dec/results_<timestamp>.csv`  
- Create a PDF report in `results/btst_v1_1dec/`  
- Generate logs in `logs/btst_v1_1dec/`  

### Analyzing Results
```python
from src.analytics import Metrics
import pandas as pd

# Load backtest results
df_results = pd.read_csv('results/btst_v1_1dec/results_20251208_190238.csv')

# Create metrics object
metrics = Metrics(df_results, initial_capital=100000)

# Generate custom report
metrics.generate_report(
strategy="BTST_V1_1DEC",
return_type="execution",  # or "gross", "net"
logic="Buy ATM CE when evening spot > morning spot",
file_path="results/btst_v1_1dec",
filename="custom_report.pdf"
)

# Access individual metrics
cagr = metrics.cagr_return_pct()
max_dd = metrics.max_drawdown_pct()
sharpe = metrics.sharpe_ratio()
```

### Creating a New Backtest

1. Copy an existing strategy folder: `cp -r strategies/btst_v1_1dec strategies/my_strategy` 
2. Modify `config.py` with your parameters
3. Update `logic.py` with your strategy logic  
4. Run `python3 main.py`


## Project Structure
```
Backtests/
├── config/                     ← NEW (entire folder)
│   ├── __init__.py
│   └── settings.py             # Framework-level settings
├── data/
│   ├── Nifty/
│   │   ├── Smaller Files/
│   │   ├── NIFTY_Expiries.csv
│   │   ├── NIFTY_Options.csv
│   │   └── NIFTY_Spot.csv
│   └── Sensex/
│       ├── SENSEX_Options.csv
│       └── SENSEX_Spot.csv
├── logs/                       ← NEW (entire folder - moved from strategy)
│   └── btst_v1_1dec/
├── results/                    ← NEW (entire folder - moved from strategy)
│   └── btst_v1_1dec/
│       ├── results_*.csv
│       └── *.pdf
├── src/
│   ├── __init__.py
│   ├── analytics.py            # Metrics and reporting
│   ├── data_operations.py      # Data loading and processing
│   └── execution.py            # Trade execution logic
├── strategies/                 ← CHANGED (was "runs/")
│   └── btst_v1_1dec/           # Example strategy
│       ├── config.py           # Strategy configuration
│       ├── logic.py            # Strategy logic
│       ├── main.py             # Execution script
│       ├── readme.md
│       └── scratch1.ipynb      # Analysis notebook
├── .gitignore
├── readme.md
└── requirements.txt
```




