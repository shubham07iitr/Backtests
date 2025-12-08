"""
This file will hold some common config settings, which can be used across different backtesting strategies
"""

import os

#--------------------------------------------------------------COMMON PATHS----------------------------------------------------------------------------------------#
# Anchor to this file's location: Backtests/config/settings.py
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))    # Backtests/config/
PROJECT_ROOT = os.path.dirname(CONFIG_DIR)                 # Backtests/

# Core directories
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
STRATEGIES_DIR = os.path.join(PROJECT_ROOT, "strategies")

#--------------------------------------------------------------COMMON DEFAULTS----------------------------------------------------------------------------------------#
# Logging
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Execution defaults (can be overridden per strategy)
DEFAULT_SLIPPAGE = 0.01
DEFAULT_INITIAL_CAPITAL = 100000
DEFAULT_RPT = 0.01  # Risk per trade