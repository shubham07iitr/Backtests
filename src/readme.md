# src/ - Core Utilities

Reusable modules for options backtesting.

---

## 📁 Files

### `execution.py`
**Class:** `Execution(slippage_pct)`  
Models transaction execution with slippage.

**Key Method:** `txn_price_simple_avg(signal, O, H, L, C)` → Returns execution price and cost

**Usage:**
```python
from execution import Execution
execution = Execution(slippage_pct=0.01)
price, cost = execution.txn_price_simple_avg("BUY", 100, 102, 99, 101)
```

---

### `data_operations.py`
**Type:** Module-level functions (stateless utilities)

**Key Functions:**
- `data_breakdown()` - Split large CSV into daily files
- `add_spot_price()` - Map spot OHLC to options data
- `add_ATM_tag_vs_spot()` - Tag ATM strikes
- `add_nearest_next_nearest_expiry()` - Map expiries
- `get_expiries()` - Extract expiry dates from instrument names

**Usage:**
```python
import data_operations as data
data.data_breakdown("NIFTY_Options.csv", "_timestamp")
df = data.add_spot_price(df, df_spot, "_timestamp", "timestamp", close=True)
```

---

### `analytics.py`
**Class:** `Metrics(df_results, initial_capital)`  
Calculates performance metrics and generates reports.

**Key Methods:**
- Returns: `total_return_pct()`, `cagr_return_pct()`
- Risk: `max_drawdown_pct()`, `sharpe_ratio()`, `calmar_ratio()`
- Win/Loss: `winrate_pct()`, `expectancy_pct()`
- Visualization: `generate_report()` - Creates full PDF report

**Usage:**
```python
from analytics import Metrics
metrics = Metrics(df_results, initial_capital=100000)
metrics.generate_report("My Strategy", "execution", filename="report.pdf")
```

---

## 📦 Dependencies
```bash
pip install pandas numpy matplotlib reportlab
```

---

## 📝 Notes
- Full documentation available in each `.py` file
- All functions include error handling and logging