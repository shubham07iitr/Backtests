##Importing the relevant libraries/packages
from datetime import datetime
import pandas as pd
import sys
import re ##regex
import os
import numpy as np
from functools import reduce ##reduce will help us club multiple filters together
import operator
import matplotlib.pyplot as plt
import logging

##Defining paths to download our own common libs
current_file = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_file, '..', '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))

##Now importing all of our common libraries for usage
from execution import Execution
import data_operations as data
from analytics import Metrics
import config 
import logic


##Now let's setup our logger
os.makedirs(config.LOG_DIR, exist_ok=True)  # Use from config
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),  # Convert string to logging level
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(config.LOG_DIR, f'run_{timestamp}.log'))  # Use from config
    ]
)
logger = logging.getLogger(__name__)

#--------------------------------------------------------------DEFINING MAIN FUNCTION NOW-----------------------------------------------------------------------------------#
def main():
    ##Starting our logic with a log
    logger.info(f"Starting: {config.STRATEGY_NAME}")
    ##Let's write all the steps and then run those one by  one
    ##Step 1 - Let's first create smaller files from big file, if smaller files folder doesn't exist already, we will create this folder in the data/Nifty folder
    if not os.path.exists(config.PATH_SMALLER_FILES):
        logger.info("Creating smaller files...")
        data.data_breakdown(config.PATH_LARGE_FILE, config.DATE_COLUMN_NAME, from_date = config.START_DATE, filename = config.DIRNAME)
    ##Step 2- Let's now generate the list of expiries from the data we have already
    list_expiries = data.get_expiries(config.PATH_LARGE_FILE, config.INSTRUMENT_COLUMN_NAME)
    ##Step 3 - Lets load all the smaller files which we created in a list of strings (list will only store the filne names) 
    csv_files = [f for f in os.listdir(config.PATH_SMALLER_FILES) if f.endswith('.csv')]
    csv_files.sort()
    ##Step 4 - Then we will load all the files in a dataframe - all 700 files to be loaded as dataframe in a list
    logger.info(f"Loading {len(csv_files)} CSV files...")
    list_df = [] ##List of dataframes which will load all the smaller files on to it
    for i in csv_files:
        list_df.append(pd.read_csv(os.path.join(config.PATH_SMALLER_FILES, i)))
    ##Step 5 - For the sake of efficiency , we will drop any row which is not 916 or 320
    list_df_drop_timestamps = [] ##Creating a new list of df which will store the list of df in which we have dropped all rows except that of 916 and 320
    for i in list_df:
        list_df_drop_timestamps.append(data.drop_timestamp_rows(
            i, 
            config.DATE_COLUMN_NAME, 
            config.LIST_TIMESTAMPS)) 
    print(list_df_drop_timestamps[2].shape)
    ##Step 6 - Now we will map nearest and next nearest expiry for each of the rows in our dataframe, this is also the step where we add the "date" column to our dataframses
    list_df_add_expiry = [] ## A new list of df, which will store all our df, but where we have mapped nearest and next nearest expiry
    for i in list_df_drop_timestamps:
        list_df_add_expiry.append(data.add_nearest_next_nearest_expiry(i, list_expiries, config.DATE_COLUMN_NAME))

    ##Step 7 - We will now map the spot price for each row in our dataframe
    df_spot = pd.read_csv(config.PATH_NIFTY_SPOT)
    list_df_add_spot = [] ## another list of df, which will have another column added - mapping of spot price
    for i in list_df_add_expiry:
        list_df_add_spot.append(data.add_spot_price(i, df_spot, config.DATE_COLUMN_NAME, config.DATE_COLUMN_NAME_NEW, open=True))

    ##Step 8 - We will now add a new column Tag, which will add the tag of ATM to the row which has the ATM strike for our dataframe
    list_df_add_atm = []
    for i in list_df_add_spot:
        list_df_add_atm.append(data.add_ATM_tag_vs_spot(i, config.THRESHOLD, config.COLUMN_SPOT_PRICE_NAME, config.COLUMN_STRIKE_NAME))

    ##Step 9 - We will now run our logic (if evening price > morning price buy ce else pe) to generate a dict of type - {date: {"Instrument": xxxyyy, "Buy Price": 1122.3, "Sell Price": 2232,4, "Buy Execution Cost": 2.2, "Sell Execution Cost": 3.2}}
    logger.info("Generating signals...")
    dict_signal = {} ## An empy dictionary to pass as param to our main function
    dict_final = logic.update_dict_signal(list_df_add_atm, dict_signal, config.MORNING_TIME, config.EVENING_TIME, config.OPTION_ENTRY_TIME, config.OPTION_EXIT_TIME, None, None, 0)
    logger.info(f"Generated {len(dict_final)} signals")
    ##Step 10 - Let;s now transform our dictionary into a dataframe with pct values
    df_results = logic.results_df(dict_final) ##in this df_results we store data in pct form
    ##Step 11 - Now let's transform our dataframe from previous step to host absolute pnl values based on risk per trade and initial capital
    df_results = logic.results_final(df_results, config.INITIAL_CAPITAL, config.RPT,config.RESULTS_FINAL_PATH)
    ##Step 12 - Finally let's use the analytics library to generate our finished pdf
    logger.info("Generating report...")
    metrics = Metrics(df_results, config.INITIAL_CAPITAL)
    metrics.generate_report( strategy = config.STRATEGY_NAME, logic = config.LOGIC, return_type = config.RETURN_TYPE, file_path = config.RESULTS_FINAL_PATH, filename= config.REPORT_NAME )
    logger.info(f"Done! Report: {config.REPORT_NAME}")
    return


if __name__ == "__main__":
    main()