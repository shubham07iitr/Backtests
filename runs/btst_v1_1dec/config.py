LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR = "logs" ##to be used for logger setup
PATH_SMALLER_FILES = "../../data/Nifty/Smaller Files" ##For step 1, to check whether folder already exists or not
PATH_LARGE_FILE = "../../data/Nifty/NIFTY_Options.csv" ## For step 1, the path where our larger file is located
DIRNAME = "Smaller Files" ##For step 1, where we want to create a directory
START_DATE = "2022-01-03" ## For step 1, we will create files only starting 3rd Jan 22
DATE_COLUMN_NAME = "_timestamp" ##For step 1, where we will pass in the column name based on which the date wise operation will happen
INSTRUMENT_COLUMN_NAME = "_instrumentname" ##For step 2, where we will extract exiry dates from the instrument names
LIST_TIMESTAMPS = ["09:16:00", "15:20:00"] ##For step 5, where we want to drop all rows which are not in the given list for efficiency
PATH_NIFTY_SPOT =  "../../data/Nifty/NIFTY_Spot.csv" #For spot 6, where we will map spot price in our list of df
DATE_COLUMN_NAME_NEW = "date" ##Useful for step 7, where we map spot price and call the add_spot_price function, we have a new column called "date" when we divided the files into smaller chunks
COLUMN_SPOT_PRICE_NAME = "spot_open_price" ## ##For step 8, to add ATM to our file , where we will run the function add_ATM_tag_vs_spot
COLUMN_STRIKE_NAME = "Strike Price" ##For step 8, to add ATM to our file , where we will run the function add_ATM_tag_vs_spot
THRESHOLD = 25 ## Fdr step 8, to determine the threshold beyond which a strike is or is not ATM
MORNING_TIME =  "09:16:00" ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values
EVENING_TIME =   "15:20:00" ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values

OPTION_EXIT_TIME = "09:16:00" ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values
OPTION_ENTRY_TIME = "15:20:00" ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values
SLIPPAGE = 0.01 ##For step 9, where we are running our updte_dict_signal function to actually create the data_dict with values

INITIAL_CAPITAL = 100000 ##For step 11, where we transform pct wise data in results_df in absolute pnl 
RPT = 0.01 ##For step 11, where we transform pct wise data in results_df in absolute pnl 

STRATEGY_NAME = "BTST_V1_1DEC" ##For step 12, where we generate the final report
LOGIC = "If evening spot price > morning spot price, but ATM CE, else buy ATM PE" ##For step 12, where we generate the final report
RETURN_TYPE = "gross" ##For step 12, we want to generate report for gross returns
REPORT_NAME = "BTST_V1_1DEC_GROSS_1.pdf"