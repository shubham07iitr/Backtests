# Data Directory

Historical options and spot data for backtesting strategies.

## IMPORTANT NOTE

- Since data is very large, we have just uploaded sample data organised in the following format:
- data>Nifty> NIFTY_Options_Sample.csv | NIFTY_Spot_Sample.csv | NIFTY_Expiries.csv
- data>Sensex>SENSEX_Options_Sample.csv | SENSEX_Spot_Sample.csv 
- To download actual 12GB data set can be downloaded from "https://drive.google.com/drive/u/0/folders/1_obGyeqqnBb6O_P8pr8TxD-PdjHLRC33"


## Data Sources

- **Provider**: [Your data source]
- **Frequency**: Intraday (minute-level timestamps)

## Date Ranges by Dataset
- **Actual data should be named like below:**

| Dataset | Start Date | End Date | Duration |
|---------|------------|----------|----------|
| NIFTY Options | 2022-01-03 | 2025-04-17 | ~3.3 years |
| NIFTY Spot | 2016-01-01 | 2025-07-11 | ~9.5 years |
| SENSEX Options | 2023-07-18 | 2025-08-08 | ~2.1 years |
| SENSEX Spot | 2021-01-01 | 2025-09-02 | ~4.7 years |

## Files

### Nifty/

#### NIFTY_Options.csv
Historical options chain data for NIFTY index

**Size**: ~12GB (full dataset)
**Period**: 2022-01-03 to 2025-04-17

**Columns** (12 total):

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `_instrumentname` | object | Option contract identifier | NIFTY31MAR2221000CE |
| `_timestamp` | object | Trade timestamp (YYYY-MM-DD HH:MM:SS) | 2022-01-03 09:15:00 |
| `_open` | float64 | Opening price | 13.25 |
| `_high` | float64 | Highest price | 13.25 |
| `_low` | float64 | Lowest price | 10.15 |
| `_close` | float64 | Closing price | 10.15 |
| `_volume` | int64 | Trading volume | 100 |
| `_oi` | int64 | Open interest | 61900 |
| `Instrument` | object | Underlying index | NIFTY |
| `Expiry` | object | Option expiry date | 2022-03-31 |
| `Strike Price` | int64 | Strike price | 21000 |
| `Option Type` | object | Call (CE) or Put (PE) | CE |

#### Smaller Files/
Daily split files of NIFTY_Options.csv for easier processing

**Structure**: `file_YYYY-MM-DD.csv`

- Same column structure as NIFTY_Options.csv
- Each file contains one day's options data
- Useful for testing or processing individual days
- Example: `file_2024-12-03.csv` contains all options data for Dec 3, 2024

#### NIFTY_Spot.csv
Intraday spot price data for NIFTY index

**Period**: 2016-01-01 to 2025-07-11

**Columns** (7 total, 5 used):

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | object | Timestamp (DD-MM-YYYY HH:MM) | 01-01-2016 09:15 |
| `open` | float64 | Opening price | 7938.45 |
| `high` | float64 | Highest price | 7939.25 |
| `low` | float64 | Lowest price | 7927.35 |
| `close` | float64 | Closing price | 7927.95 |
| `Unnamed: 5` | float64 | Unused (NaN values) | - |
| `Unnamed: 6` | float64 | Unused (NaN values) | - |

#### NIFTY_Expiries.csv
List of all NIFTY option expiry dates

**Columns** (1 total):

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `expiry_date` | object | Option expiry date (YYYY-MM-DD) | 2022-01-06 |

**Purpose**: Reference file for weekly/monthly option expiries

### Sensex/

#### SENSEX_Options.csv
Historical options chain data for SENSEX index

**Period**: 2023-07-18 to 2025-08-08

**Note**: Different column naming convention than NIFTY data (no underscores prefix, snake_case)

**Columns** (10 total):

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `datetime` | object | Trade timestamp (YYYY-MM-DD HH:MM:SS) | 2023-11-03 11:27:59 |
| `open` | float64 | Opening price | 3303.45 |
| `high` | float64 | Highest price | 3376.2 |
| `low` | float64 | Lowest price | 3303.45 |
| `close` | float64 | Closing price | 3376.2 |
| `volume` | int64 | Trading volume | 200 |
| `oi` | int64 | Open interest | 0 |
| `strike_price` | int64 | Strike price | 61100 |
| `option_type` | object | Call (CE) or Put (PE) | CE |
| `expiry` | object | Option expiry date (DDMMMYY) | 03NOV23 |

#### SENSEX_Spot.csv
Intraday spot price data for SENSEX index

**Period**: 2021-01-01 to 2025-09-02

**Columns** (7 total):

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | object | Timestamp (YYYY-MM-DD HH:MM:SS) | 2021-01-01 09:15:00 |
| `open` | float64 | Opening price | 47785.28 |
| `high` | float64 | Highest price | 47885.96 |
| `low` | float64 | Lowest price | 47772.93 |
| `close` | float64 | Closing price | 47860.46 |
| `volume` | int64 | Trading volume | 0 |
| `token` | int64 | Token identifier | 265 |

## Known DATA ISSUES/INCONSISTENCIES

### NIFTY_Options.csv

#### Incomplete Data (Partial Trading Days)

| Date | Day | Issue | Impact |
|------|-----|-------|--------|
| 2024-03-02 | Saturday | Only 107 entries until 12:30, no 15:20 data | Cannot take new positions at 15:20 |
| 2024-05-04 | Saturday | Incomplete data, no 15:20 data | Cannot take new positions at 15:20 |

**Note**: These dates are excluded from backtests requiring end-of-day positions (e.g., BTST strategies).

#### Completely Missing Data (Full Trading Days)

| Date | Day | Impact on Backtesting |
|------|-----|----------------------|
| 2023-02-16 | Thursday (Expiry) | BTST entry from Feb 15 cannot be exited |
| 2023-06-28 | Wednesday | BTST entry from Jun 27 cannot be exited |
| 2023-06-29 | Thursday | Multi-day impact on strategies |
| 2023-07-27 | Thursday (Expiry) | BTST entry from Jul 26 cannot be exited |
| 2023-11-23 | Thursday | BTST entry from Nov 22 cannot be exited |
| 2023-11-24 | Friday | Multi-day impact on strategies |
| 2025-03-13 | Thursday (Expiry) | BTST entry from Mar 12 cannot be exited |

#### Minimal Missing Timestamps

| Date | Missing Timestamps | Impact |
|------|-------------------|--------|
| 2024-08-08 | 09:15, 09:16 | BTST entry from Aug 7 cannot be exited at market open |

**Impact on Backtesting**:
- Strategies requiring exit positions on these dates will have incomplete results
- BTST (Buy Today Sell Tomorrow) strategies are particularly affected
- Total affected trading days: **9 days** out of ~800 trading days (~1.1% data loss)
- Recommended: Exclude or handle these dates explicitly in backtest logic

**Mitigation**:
- Check for missing dates before running backtests
- Log excluded trades due to missing data
- Consider forward-filling positions or skipping trades on known missing dates



## Usage
```python
import pandas as pd

# Load NIFTY options
df_nifty_opt = pd.read_csv('data/Nifty/NIFTY_Options.csv')
df_nifty_opt['_timestamp'] = pd.to_datetime(df_nifty_opt['_timestamp'])

# Load NIFTY spot (note different date format)
df_nifty_spot = pd.read_csv('data/Nifty/NIFTY_Spot.csv')
df_nifty_spot['date'] = pd.to_datetime(df_nifty_spot['date'], format='%d-%m-%Y %H:%M')

# Load SENSEX options (note different column names)
df_sensex_opt = pd.read_csv('data/Sensex/SENSEX_Options.csv')
df_sensex_opt['datetime'] = pd.to_datetime(df_sensex_opt['datetime'])

# Load SENSEX spot
df_sensex_spot = pd.read_csv('data/Sensex/SENSEX_Spot.csv')
df_sensex_spot['date'] = pd.to_datetime(df_sensex_spot['date'])

# Load single day from Smaller Files
df_single_day = pd.read_csv('data/Nifty/Smaller Files/file_2024-12-03.csv')

# Filter for ATM options
nifty_atm = df_nifty_opt[(df_nifty_opt['Strike Price'] == 21000) & 
                         (df_nifty_opt['Option Type'] == 'CE')]

sensex_atm = df_sensex_opt[(df_sensex_opt['strike_price'] == 61100) & 
                           (df_sensex_opt['option_type'] == 'CE')]
```


## Important Notes

### Column Name Differences

**NIFTY vs SENSEX Options:**

| NIFTY | SENSEX |
|-------|--------|
| `_timestamp` | `datetime` |
| `_open`, `_high`, `_low`, `_close` | `open`, `high`, `low`, `close` |
| `_volume`, `_oi` | `volume`, `oi` |
| `Strike Price` | `strike_price` |
| `Option Type` | `option_type` |
| `Expiry` | `expiry` |
| Has `_instrumentname` | No instrument name column |
| Has `Instrument` column | No underlying column |

**NIFTY vs SENSEX Spot:**

| NIFTY_Spot | SENSEX_Spot |
|------------|-------------|
| Date format: `DD-MM-YYYY HH:MM` | Date format: `YYYY-MM-DD HH:MM:SS` |
| Has `Unnamed: 5`, `Unnamed: 6` (unused) | Has `volume`, `token` columns |

### Date Format Differences

- **NIFTY_Spot.csv**: `DD-MM-YYYY HH:MM` (e.g., 01-01-2016 09:15)
- **NIFTY_Options.csv timestamp**: `YYYY-MM-DD HH:MM:SS` (e.g., 2022-01-03 09:15:00)
- **NIFTY_Options.csv expiry**: `YYYY-MM-DD` (e.g., 2022-03-31)
- **SENSEX_Spot.csv**: `YYYY-MM-DD HH:MM:SS` (e.g., 2021-01-01 09:15:00)
- **SENSEX_Options.csv datetime**: `YYYY-MM-DD HH:MM:SS` (e.g., 2023-11-03 11:27:59)
- **SENSEX_Options.csv expiry**: `DDMMMYY` (e.g., 03NOV23)

### Data Coverage

- **NIFTY Spot data**: Longest history (~9.5 years from 2016)
- **NIFTY Options data**: ~3.3 years (2022-2025)
- **SENSEX Spot data**: ~4.7 years (2021-2025)
- **SENSEX Options data**: Shortest history (~2.1 years from 2023)
- Date ranges differ between datasets - check ranges before running backtests across both indices

### General Notes

- All timestamps are in IST (Indian Standard Time)
- Spot data includes minute-level intraday prices
- Open Interest (`_oi` / `oi`) represents number of outstanding contracts
- Strike prices are in index points
- Expiries typically occur weekly (Thursday) and monthly (last Thursday)
- Use "Smaller Files" for quick testing or when working with limited memory
- Unused columns (Unnamed: 5, Unnamed: 6) in NIFTY_Spot.csv can be ignored or dropped
- SENSEX_Spot volume and token columns may be useful for additional analysis