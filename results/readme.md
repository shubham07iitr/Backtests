# Results Directory

This directory contains backtest outputs (CSV data and PDF reports) for all strategies, organized by strategy name.

## Structure
```
results/
└── <strategy_name>/
    ├── results_<timestamp>.csv
    └── <REPORT_NAME>.pdf
```

**Example:**
```
results/
└── btst_v1_1dec/
    ├── results_20251208_185859.csv
    ├── results_20251208_190238.csv
    ├── BTST_V1_1DEC_GROSS_1.pdf
    └── BTST_V1_1DEC_GROSS_2.pdf
```

## File Types

### CSV Files (`results_<timestamp>.csv`)
Contains daily PnL data with columns:
- **date**: Trading date (YYYY-MM-DD)
- **gross_pnl**: PnL before slippage and transaction costs
- **execution_pnl**: PnL after slippage, before transaction costs
- **net_pnl**: PnL after slippage and transaction costs
This may differ based on strategy tested

**Example:**
```csv
date,gross_pnl,execution_pnl,net_pnl
2022-01-03,125.50,118.30,112.80
2022-01-04,-85.20,-91.40,-95.60
2022-01-05,210.75,198.20,189.50
```

### PDF Reports (`<STRATEGY_NAME>_<RETURN_TYPE>_<VERSION>.pdf`)
Professional backtest report containing:
- **Metadata**: Strategy name, period, capital, trade count
- **Performance Charts**: Equity curve and drawdown visualization
- **Key Metrics**:
  - Returns: Total return, CAGR
  - Risk: Max drawdown, Calmar, Sharpe, Sortino ratios
  - Win/Loss: Win rate, avg win/loss, expectancy
- **Monthly Returns Heatmap**: Color-coded performance grid

## Usage

### Load Results in Python
```python
import pandas as pd

# Load specific backtest
df = pd.read_csv('results/btst_v1_1dec/results_20251208_190238.csv')

# View summary
print(df.describe())
print(f"Total PnL: ${df['net_pnl'].sum():,.2f}")
```

### Analyze with Metrics Class
```python
from src.analytics import Metrics

df = pd.read_csv('results/btst_v1_1dec/results_20251208_190238.csv')
metrics = Metrics(df, initial_capital=100000)

# Get key metrics
print(f"CAGR: {metrics.cagr_return_pct()[2]:.2%}")  # [2] = net
print(f"Max DD: {metrics.max_drawdown_pct()[2]:.2%}")
print(f"Sharpe: {metrics.sharpe_ratio()[2]:.2f}")
print(f"Win Rate: {metrics.winrate_pct()[2]:.2%}")
```

### Compare Multiple Runs
```bash
# List all results
ls -lth results/btst_v1_1dec/

# Compare file sizes
du -sh results/btst_v1_1dec/*.csv
```

### Clean Old Results
```bash
# Keep only last 5 results
cd results/btst_v1_1dec/
ls -t results_*.csv | tail -n +6 | xargs rm
ls -t *.pdf | tail -n +6 | xargs rm
```

## Configuration

Results output is controlled in `strategies/<strategy_name>/config.py`:
```python
# Where results are saved
RESULTS_FINAL_PATH = os.path.join(settings.RESULTS_DIR, STRATEGY_FOLDER)

# Report configuration
RETURN_TYPE = "gross"  # Options: "gross", "execution", "net"
REPORT_NAME = "BTST_V1_1DEC_GROSS_2.pdf"
```

## Return Types Explained

| Type | Description | Use Case |
|------|-------------|----------|
| **gross** | PnL before slippage/costs | Theoretical best case |
| **execution** | PnL after slippage | Realistic with slippage model |
| **net** | PnL after all costs | Most conservative estimate |

## Notes

- ✅ Results are automatically generated on each backtest run
- ✅ Timestamped CSV filenames prevent overwriting
- ✅ This directory is **gitignored** (results are not committed)
- ✅ Safe to delete old results - regenerate by re-running backtest
- ⚠️ Large CSV files (>100MB) may slow down analysis - consider filtering data