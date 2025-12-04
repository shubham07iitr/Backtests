##Importing the relevant libraries/packages
import pandas as pd
import re ##regex
import os
import numpy as np
from functools import reduce ##reduce will help us club multiple filters together
import operator

##Settingup the logger
import logging
logger = logging.getLogger(__name__)


##WE DECIDED TO NOT HAVE A CLASS HERE AS NO ATTRIBUTES WILL BE NEEDED 
        
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
"""
Signature:
    Inputs:
        path (String) - path representing the path on our file system where the larger file is located for e.g "../../data/Nifty/NIFTY_Options.csv"
        date_column_name (String) - Actual name of the column which has datetime data in the form "YYYY-MM-DD" format
        from_date (String) - Optional argument - Date passed as string in "YYYY-MM-DD" format - basically the date from which we want to start the file creation
        to_date (String) Optional argument - Date passed as string in "YYYY-MM-DD" format - basically the date till which we want to finish the file creation
        filename (String) Optional argument - by defaile will be "Smaller Files" else whatever the user passes in 
    Outputs: 
        A new folder called 'Smaller Files' with mutliple csv files named 'file_yyyy_mm_dd' will be created on which we could operate independently
Purpose: To transform a big csv file into multiple smaller files based on each day which could be loaded up in RAM separately for smoother operations
    Both from_date and to_date are optional , it both are not present, it will create files from start till end, if only one/both present then will take action accordingly
    Will do error hadnling as well, for eg. if someone passes 2100-01-90 etc
    The new folder will be created in teh same path as where our bigger file is lcoated - the path param which is being passed through    
"""

def data_breakdown(path, date_column_name, from_date=None, to_date=None, filename="Smaller Files"):
    
    chunk_size = 10000
    # Check if input file exists
    if not os.path.exists(path):
        logger.error(f"Input file not found: {path}")  # ADDED
        raise FileNotFoundError(f"Input file not found: {path}")
    
    # Get the directory where the input file is located
    input_directory = os.path.dirname(os.path.abspath(path))
    
    # Create the output folder path in the same directory as input file
    output_folder = os.path.join(input_directory, filename)
    
    # Error handling for date parameters
    try:
        if from_date is not None:
            from_date = pd.to_datetime(from_date).normalize()
        if to_date is not None:
            to_date = pd.to_datetime(to_date).normalize()
    except Exception as e:
        logger.error(f"Invalid date format: {e}")  # ADDED
        raise ValueError(f"Invalid date format. Please use 'YYYY-MM-DD' format. Error: {e}")
    
    # Validate date range
    if from_date is not None and to_date is not None:
        if from_date > to_date:
            logger.error("from_date cannot be greater than to_date")  # ADDED
            raise ValueError("from_date cannot be greater than to_date")
    
    # Creating smaller files folder with custom name in the same directory as input
    os.makedirs(output_folder, exist_ok=True)
    
    # For each chunk, we will do a groupby based on date, and if the file already exists for that group will append to the file, else we will create a new file
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        try:
            chunk["date"] = pd.to_datetime(chunk[date_column_name]).dt.normalize()
        except Exception as e:
            logger.error(f"Error parsing date column '{date_column_name}': {e}")  # ADDED
            raise ValueError(f"Error parsing date column '{date_column_name}': {e}")
        
        # Filter based on from_date and to_date
        if from_date is not None:
            chunk = chunk[chunk["date"] >= from_date]
        if to_date is not None:
            chunk = chunk[chunk["date"] <= to_date]
        
        # Skip if chunk is empty after filtering
        if chunk.empty:
            continue
        
        for name, group in chunk.groupby("date"):
            file_path = os.path.join(output_folder, f"file_{name.date()}.csv")
            file_exists = os.path.exists(file_path)
            # Remove the temporary date column before saving
            group_to_save = group.drop("date", axis=1)
            group_to_save.to_csv(file_path,
                                mode='a' if file_exists else 'w',
                                header=not file_exists,
                                index=False)
    
    logger.info(f"Files created successfully in: {output_folder}")  # CHANGED from print
    return
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
"""
Signature:
    Inputs: 
        file_path (String): Path of the file in which data is stored (String)
        instrument_column (String): Name of the column in which instrument name is stored, instrument name should typically be in form of "NIFTY31MAR2221000CE"
    Output: 
        list_expiries (List of strings) : List of expiries in "YYYY-MM-DD" format - all are strings
        The regex pattern currently works to identify only years from 2022-2025, we can modify by changing 2[2-5] pattern in regex match
Purpose: To get the unique list of expiries from a given data set (and will be outputted as a list of strings of unique expiries)
"""
def get_expiries(file_path, instrument_column):
    ##Reading the file from the path, but only the instrument colum and capturing the unique instruments
    df = pd.read_csv(file_path, usecols = [instrument_column])
    list_instruments = df["_instrumentname"].unique()
    list_expiries = []
    ##Looping over list of unique instruemnts, to apply regex logic to get our expiry patterns, and then finding unique on them using set conversions (Set can only hold unique data)
    for i in list_instruments:
        a = re.search(r"^.*([0-3][0-9][A-Z]{3}2[2-5]).*$", i)
        if a:
            list_expiries.append(str(pd.to_datetime(a.group(1)))[0:10])
        temp_set = set(list_expiries)
        list_expiries = list(temp_set)
    return list_expiries

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
"""
Signature:
    Inputs:
        df_temp (Pandas DF): DF in which we want to map the nearest expiry
        list_expiries (LIst of strings): LIst of all expiry days , should cover expiries at least or more than the scope of datetimes in df_temp and should be in string format
        date_column ("String") : Name of the column which has the datetimestamp against which we want to map the nearest expiry, the dtype of the column should be object
    Output: 
        df_temp(Pandas DF): Returns a new df with two new columns added at the end called "nearest_expiry" and next_nearest_expiry (a datetime object) which captures the nearest and next nearest expiries to each row in the given df
Purpose: 
"""
def add_nearest_next_nearest_expiry(df_temp, list_expiries, date_column):
    ##We add a new column date which will convert the object type of date column to actual date time
    df_temp["date"] = pd.to_datetime(df_temp[date_column]).dt.normalize()

    # Prepare expiries - again converting string expiries to date objects
    new_list_expiries = sorted([pd.to_datetime(i).normalize() for i in list_expiries])
    
    # Find both nearest and next nearest in one pass
    ##We first identify all expiries which are higher than current times and then pick the first and second one
    def find_both_expiries(date):
        future = [e for e in new_list_expiries if e >= date]
        if not future:
            return None, None
        # Nearest is the first one (list is sorted)
        nearest = future[0].date()
        # Next nearest is the second one (if exists)
        next_nearest = future[1].date() if len(future) > 1 else None
        return nearest, next_nearest
    # Apply and unpack
    df_temp[["nearest_expiry", "next_nearest_expiry"]] = df_temp["date"].apply(
        lambda x: pd.Series(find_both_expiries(x))
    )
    
    return df_temp

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
"""
Signature:
    Inputs:
        df_options (Pandas DF): DF which has options data
        df_spot (Pandas DF): DF which has spot data
            df_spot should have the columns "open", "high", "low", "close"
        data_column_options (String): name of the column for df_options which has min by min data (but stored as object) such as 01-01-2016 09:15
        data_column_spot (String): name of the column for df_spot which has min by min data (but stored as object) such as 01-01-2016 09:15
            Expected format for date in df_spot would be format="%d-%m-%Y %H:%M"
        open, high, low, close (Boolean): Names of the prices to tbe added
    Outputs:
        df_options (Pandas df): with one to 4 new columns added for which of the price points to be added

Purpose: Map the spot price (OHLC) for every corresponding timeseries row
"""


def add_spot_price(df_options, df_spot, date_column_options, date_column_spot, open=False, high = False, low = False, close = False ):
    ##Below approach was extremely slow so updated to vectorised approach by direct operations on df series, rather than looping over
    ##Getting the right datetime formats for both dataframes
    """
    df_options[date_column_options] = pd.to_datetime(df_options[date_column_options])
    df_spot[date_column_spot] = pd.to_datetime(df_spot[date_column_spot], format="%d-%m-%Y %H:%M")
    ##Now writing if conditionals for whhich all price points to be added
    if open:
        list_price = [] ##list of dictionaries
        for index, row in df_spot.iterrows():
            list_price.append({row[date_column_spot]: row["open"]})
        df_options["spot_open_price"] = df_options[date_column_options].map({k: v for d in list_price for k, v in d.items()}) ## here we are creating a new dictionary for mapping directly, much ewasier to do            
    if high:
        list_price = [] ##list of dictionaries
        for index, row in df_spot.iterrows():
            list_price.append({row[date_column_spot]: row["high"]})
        df_options["spot_close_price"] = df_options[date_column_options].map({k: v for d in list_price for k, v in d.items()})
    if low:
        list_price = [] ##list of dictionaries
        for index, row in df_spot.iterrows():
            list_price.append({row[date_column_spot]: row["low"]})
        df_options["spot_low_price"] = df_options[date_column_options].map({k: v for d in list_price for k, v in d.items()})    
    if close:
        list_price = [] ##list of dictionaries
        for index, row in df_spot.iterrows():
            list_price.append({row[date_column_spot]: row["close"]})
        df_options["spot_open_price"] = df_options[date_column_options].map({k: v for d in list_price for k, v in d.items()})
    return df_options
    """
    df_options[date_column_options] = pd.to_datetime(df_options[date_column_options])
    df_spot[date_column_spot] = pd.to_datetime(df_spot[date_column_spot], format="%d-%m-%Y %H:%M")
    # Remove duplicates - keep='last' keeps the most recent value for duplicate timestamps
    df_spot_unique = df_spot.drop_duplicates(subset=[date_column_spot], keep='last')
    # Create mapping Series - USE df_spot_unique, not df_spot!
    spot_indexed = df_spot_unique.set_index(date_column_spot)  # ✅ Fixed!
    if open:
        df_options["spot_open_price"] = df_options[date_column_options].map(spot_indexed["open"])
    if high:
        df_options["spot_high_price"] = df_options[date_column_options].map(spot_indexed["high"])
    if low:
        df_options["spot_low_price"] = df_options[date_column_options].map(spot_indexed["low"])
    if close:
        df_options["spot_close_price"] = df_options[date_column_options].map(spot_indexed["close"])
    
    return df_options

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

"""
Signature:
    Inputs:
        df_options(Pandas DF): the df on which we want to add a new tag column, should already have the spot price column
        threshold. (Int): this is basically the threshold delta using which we decide whether a given strike price is ATM or not, for e.g. for NF it will be 25, for BN 100, for SS 100
        column_spot_price(String): Name of the column in which we have the spot price against which we want to calibrate
        column_trike_price(String): Name of the column in which we have the Strike price for which we want to add the relevant data 

    Output:
        df_options (Pandas DF): with one column added at the end called "Tag"
Purpose: To add ATM tag for all strikes which are currently ATM at that time, will be added None if it is not ATM
"""

def add_ATM_tag_vs_spot(df_options, threshold, column_spot_price, column_strike_price):
    df_options["Tag"] = np.where(abs(df_options[column_strike_price] - df_options[column_spot_price]) <= threshold, "ATM", None) ##Using vectorised operations through NP
    return df_options

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

"""
Signature:
    Inputs:
        df_options (Pandas DF): The df in which we want to add another column of expiry (it should already have the instrument name column)
        column_instrument (String): Name of the column in df_options which has the instrument name (should be similar to "NIFTY01FEB2419500CE")
    Outputs:
        df_options (Pandas DF): with one more column called "Expriry" which will have dates in object format like "2024-02-01" basically "YYYY-MM-DD"
Purpose: To add a new column to the existing df called "Expiry" by extracting the date from the insturment name column (will add None if pattern match not succesful)
"""

def add_expiry_column(df_options, column_instrument):
    ##We define a new function which will called along with apply when operating on the new column on the DF
    def get_expiry(instrument_name):
        a = re.search(r"^.*([0-3][0-9][A-Z]{3}2[2-5]).*$", instrument_name)
        if a:
            return str(pd.to_datetime(a.group(1)))[0:10]
        else:
            return None
    ##Now we apply this function to our actual df
    df_options["Expiry"] = df_options[column_instrument].apply(get_expiry)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

"""
Signature:
    Inputs:
        df_options (Pandas DF): The df in which we want to drop the rows from 
        column_date (String) : Name of the column on which we will compare and operate on 
            Date inside the column should be in teh format: "2022-01-06 09:15:00" as string/objects
        list_of_timestampes (List Strings): LIst of timestamps which we want to keep in our df, should be of the format "09:15:00" as string
    Output:
        df_new(Pandas DF): A new df called df_new which will have lesser rows because some of it would have been filtered out
    Purpose: To filter out any rows which may not be useful for our computation based on the list of timestamps provided in the input params, since we are dropping rows, hence we will reset index here
"""

def drop_timestamp_rows(df_new, column_date, list_of_timestamps):
    ##First let's combine all the filters as a series of booleans for each of the timestamps 
    filters = [df_new[column_date].str.endswith(t) for t in list_of_timestamps] 
    ##Let's then combine all the filters in a single OR filter like filter 1 | filter 2 | filter 3 etc and then apply those on the df
    combined_filter = reduce(operator.or_, filters) ##
    df_new = df_new[combined_filter]
    df_new.reset_index(inplace = True)
    return df_new

            

                            


                
                
