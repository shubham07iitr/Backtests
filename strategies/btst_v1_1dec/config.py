# strategies/btst_v1_1dec/config.py
import os
import sys

# Import framework settings from root>config>settings.py
current_file = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_file, '..', '..', 'config')
sys.path.insert(0, os.path.abspath(config_path))
import settings

#--------------------------------------------------------------GENERIC CONFIGS----------------------------------------------------------------------------------------#
LOG_LEVEL = settings.LOG_LEVEL   # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL ##Currently inheriting from settings.py, but can override
# Strategy identification (define once, reuse everywhere)
STRATEGY_FOLDER = "btst_v1_1dec"  # For folder paths to be reused in paths

#--------------------------------------------------------------DEFINING PATHS FOR MAIN.PY------------------------------------------------------------------------------#
LOG_DIR = os.path.join(settings.LOGS_DIR, STRATEGY_FOLDER) ##to be used for logger setup (step 0)
PATH_SMALLER_FILES = os.path.join(settings.DATA_DIR, "Nifty", "Smaller Files") ##For step 1, to check whether folder already exists or not
PATH_LARGE_FILE = os.path.join(settings.DATA_DIR, "Nifty", "NIFTY_Options.csv") ## For step 1, the path where our larger file is located
PATH_NIFTY_SPOT =  os.path.join(settings.DATA_DIR, "Nifty", "NIFTY_Spot.csv") #For spot 6, where we will map spot price in our list of df
RESULTS_FINAL_PATH = os.path.join(settings.RESULTS_DIR, STRATEGY_FOLDER) ##For step 11, where we will store 3 things (PDF report, results csv, and equity + dd curve png file)

#--------------------------------------------------------------INPUT SPECIFIC CONFIGS-----------------------------------------------------------------------------------#
##These include name of the different files/columns etc. which are being put into the input
##Data column name and structure
DATE_COLUMN_NAME_NEW = "date" ##Useful for step 7, where we map spot price and call the add_spot_price function, we have a new column called "date" when we divided the files into smaller chunks
COLUMN_SPOT_PRICE_NAME = "spot_open_price" ## ##For step 8, to add ATM to our file , where we will run the function add_ATM_tag_vs_spot
COLUMN_STRIKE_NAME = "Strike Price" ##For step 8, to add ATM to our file , where we will run the function add_ATM_tag_vs_spot
DATE_COLUMN_NAME = "_timestamp" ##For step 1, where we will pass in the column name based on which the date wise operation will happen
INSTRUMENT_COLUMN_NAME = "_instrumentname" ##For step 2, where we will extract exiry dates from the instrument names

##Data filtering
START_DATE = "2022-01-03" ## For step 1, we will create files only starting 3rd Jan 22
LIST_TIMESTAMPS = ["09:16:00", "15:20:00"] ##For step 5, where we want to drop all rows which are not in the given list for efficiency

#--------------------------------------------------------------STRAT SPECIFIC CONFIGS-----------------------------------------------------------------------------------#
##These include strat sepcfic configs such as what should be entry time, exit time, 
THRESHOLD = 25 ## Fdr step 8, to determine the threshold beyond which a strike is or is not ATM
MORNING_TIME =  "09:16:00" ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values
EVENING_TIME =   "15:20:00" ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values
OPTION_EXIT_TIME = "09:16:00" ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values
OPTION_ENTRY_TIME = "15:20:00" ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values
SLIPPAGE = settings.DEFAULT_SLIPPAGE ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values
INITIAL_CAPITAL = settings.DEFAULT_INITIAL_CAPITAL ##For step 11, where we transform pct wise data in results_df in absolute pnl 
RPT = settings.DEFAULT_RPT ##For step 11, where we transform pct wise data in results_df in absolute pnl 

#--------------------------------------------------------------OUTPUT SPECIFIC CONFIGS-----------------------------------------------------------------------------------#
##These include params such as what should be output file name/report name etc. (does not directly impact logic of the strategy)
DIRNAME = "Smaller Files" ##For step 1, where we want to create a directory
STRATEGY_NAME = "BTST_V1_1DEC" ##For step 12, where we generate the final report
LOGIC = "If evening spot price > morning spot price, but ATM CE, else buy ATM PE" ##For step 12, where we generate the final report
RETURN_TYPE = "gross" ##For step 12, we want to generate report for gross returns
REPORT_NAME = "BTST_V1_1DEC_GROSS_2.pdf"


















