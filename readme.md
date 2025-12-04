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

Navigate to a specific backtest folder and run:
```bash
cd runs/btst_v1_1dec
python3 main.py
```

This will:
- Execute the backtest using the strategy defined in `logic.py`
- Use parameters from `config.py`
- Generate `results.csv` with daily PnL
- Create a PDF report with metrics and charts

### Analyzing Results
```python
from src.analytics import Metrics
import pandas as pd

# Load backtest results
df_results = pd.read_csv('runs/btst_v1_1dec/results.csv')

# Create metrics object
metrics = Metrics(df_results, initial_capital=100000)

# Generate custom report
metrics.generate_report(
    strategy="BTST_V1_1DEC",
    return_type="execution",  # or "gross", "net"
    logic="Buy ATM CE when evening spot > morning spot",
    filename="custom_report.pdf"
)

# Access individual metrics
cagr = metrics.cagr_return_pct()
max_dd = metrics.max_drawdown_pct()
sharpe = metrics.sharpe_ratio()
```

### Creating a New Backtest

1. Copy an existing backtest folder
2. Modify `config.py` with your parameters
3. Update `logic.py` with your strategy
4. Run `python3 main.py`


## Project Structure
```
Backtests/
├── data/
│   ├── Nifty/
│   │   ├── Smaller Files/
│   │   ├── NIFTY_Expiries.csv # File with all NIFTY expiries since 2022
│   │   ├── NIFTY_Options.csv
│   │   └── NIFTY_Spot.csv
│   └── Sensex/
│       ├── SENSEX_Options.csv
│       └── SENSEX_Spot.csv
├── runs/
│   └── btst_v1_1dec/          # Example backtest run
│       ├── config.py           # Strategy configuration
│       ├── logic.py            # Strategy logic
│       ├── main.py             # Execution script
│       ├── results.csv         # Backtest results
│       ├── report.pdf          # Generated PDF report
│       └── scratch1.ipynb      # Analysis notebook
├── src/
│   ├── __init__.py
│   ├── analytics.py            # Metrics and reporting
│   ├── data_operations.py      # Data loading and processing
│   └── execution.py            # Trade execution logic
├── readme.md
└── requirements.txt
```




