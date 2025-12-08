# Logs Directory

This directory contains execution logs for all backtest runs, organized by strategy.

## Structure
```
logs/
└── <strategy_name>/
    └── run_<timestamp>.log
```

**Example:**
```
logs/
└── btst_v1_1dec/
    ├── run_20251208_185859.log
    ├── run_20251208_190238.log
    └── run_20251208_193045.log
```

## Log Contents

Each log file captures:
- **INFO**: Strategy execution progress (loading data, generating signals, creating reports)
- **WARNING**: Missing data, skipped trades, incomplete executions
- **ERROR**: Critical failures (missing files, invalid configurations)
This format may be overridden for some specific strategies

## Log Format
``` 
HH:MM:SS - LEVEL - MESSAGE (Again may be overridden for some specific strat)
```

**Example:**
```
19:02:38 - INFO - Starting: BTST_V1_1DEC
19:02:39 - INFO - Creating smaller files...
19:03:12 - INFO - Loading 734 CSV files...
19:03:45 - INFO - Generating signals...
19:03:46 - WARNING - Skipping 2022-01-05 - spot price not found
19:04:02 - INFO - Generated 689 signals
19:04:03 - WARNING - Filtered 3 incomplete trades (no exit)
19:04:04 - INFO - Generating report...
19:04:06 - INFO - Done! Report: BTST_V1_1DEC_GROSS_2.pdf
```

## Usage

### View Latest Log
```bash
# Linux/Mac
tail -f logs/btst_v1_1dec/run_*.log | tail -1

# Or view specific log
cat logs/btst_v1_1dec/run_20251208_190238.log
```

### Search for Errors
```bash
grep "ERROR" logs/btst_v1_1dec/*.log
grep "WARNING" logs/btst_v1_1dec/*.log
```

### Clean Old Logs
```bash
# Keep only last 10 logs
cd logs/btst_v1_1dec/
ls -t | tail -n +11 | xargs rm
```

## Configuration

Log level is set in `strategies/<strategy_name>/config.py`:
```python
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Log Levels:**
- **DEBUG**: Detailed diagnostic information
- **INFO**: General execution flow (default)
- **WARNING**: Something unexpected but not fatal
- **ERROR**: Serious problem, execution may fail
- **CRITICAL**: Catastrophic failure

## Notes

- ✅ Logs are automatically created on each backtest run
- ✅ Timestamped filenames prevent overwriting
- ✅ Safe to delete old logs - they're regenerated on next run