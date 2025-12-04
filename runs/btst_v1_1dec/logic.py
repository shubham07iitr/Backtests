"""
This will will caputre all the strategy specific functions which we will be using in the main.py file
"""

##Importing the relevant libraries/packages
import pandas as pd
import re ##regex
import os
import sys
import numpy as np
from functools import reduce ##reduce will help us club multiple filters together
import operator
import config
current_file = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_file, '..', '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))

# Now import your functions
from execution import Execution

##Creating the object for using the Execution methods (and using the slippage from config files)
execution = Execution(config.SLIPPAGE)

##Defining our logger
import logging
logger = logging.getLogger(__name__)

"""
Singature:
    Inputs:
        df_options (Pandas df): The df from which we will capture the spot price values, it must have the following values/columns:
            "_timestamp" colunm which will have string level datetimestamp values such as "2024-01-25 09:16:00"
            "spot_open_price" column which will have float level valyes for spot price at the given stamp
        morning_time (String): Should be in string format but representing time such as "09:16:00"
        evening_time (String): Should be in string format but representing time such as "15:16:00"
        date (String): Should be of the form String of format: "YYYY-MM-DD"
    Outputs:
        (morning_price, evening_price) (Tuple of floats):  will return the price of spot as a tuple for the given two values of morning and evening times
Purpose: 
    To get values of 916 spot "open" price and 320 spot "open" price as a tuple
    Since this sheet is specific to this run, hence not looking to make it too scaleable
"""

def get_entry_exit_spot(df_options, morning_time, evening_time, date):
    ##We first get the filtered timeframes (this is done to ensure there are no empty vales for spot)
    evening_filtered = df_options[df_options["_timestamp"] == date+" "+evening_time]  # ADDED
    morning_filtered = df_options[df_options["_timestamp"] == date+" "+morning_time]  # ADDED
    ##If we cannt find morning or evening spot price we will return None
    if len(evening_filtered) == 0 or len(morning_filtered) == 0:  # ADDED
        logger.warning(f"Missing spot price for {date}")  # ADDED
        return None, None  # ADDED
    ##Else we will return the spot open price
    evening_price = evening_filtered["spot_open_price"].values[0]  # CHANGED
    morning_price = morning_filtered["spot_open_price"].values[0]  # CHANGED
    return (morning_price, evening_price)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

"""
Singature:
    Inputs:
        df_options(Pandas df): The df on which we will operate on, should have the following fields which we will be using:
            Column "_timestamp" of string/object dtype which will have values of type "2024-01-25 15:20:00"
            Column "Tag" of object type: - which will have "ATM" for a strike which is ATM, or will have None
            Column "Option Type" of object type - which will have either CE or PE
            Column "_instrumentname" of object type:  which will have the name of the instrument we are trading such as "NIFTY03FEB2217800CE"
            Column "date" which will be of pandas datetime datateype and will have values like "2022-01-07" and represents the date on which trading is happening
            Column "nearest_expiry" and "next_nearest_expiry" which will be of pbject dtype but will store dates such as "2022-01-07"
        dict_signal (Dictioary):  which will be of type {date: {"Instrument": xxxyyy, "Buy Price": 1122.3, "Sell Price": 2232,4, "Buy Execution Cost": 2.2, "Sell Execution Cost": 3.2}} and will be updated for each day
            For dict_signal , date will be of type python date
        signal (String): Should be either "PE" or "CE" to indicate whether we are buying a put or a call option 
        entry_time (String): Should be a string representing when we are looking to buy our ce/pe of the form "09:16:00"
    Outputs:
        dict_signal (Dictionary): The dictionary which was passed in as input, we will return as output with adding the instument, and buy price, and buy execution cost
        instrument (Stirng) : The instrument which was bought for the date
        date_trade (Datetime python): The date on which the trade was taken 
Purpose:
    This function is intended to update the input dictionary for us of the form {date: {"Instrument": xxxyyy, "Buy Price": 1122.3, "Sell Price": 2232,4}}
    This function will only update date, instrument, buy price, sell price and pnl will be separately updated in a different function
    But wll return the instrument, and the date of trade, which will serve as the input for our dict_signal_sell function
"""
def dict_signal_buy(df_options, dict_signal, signal, entry_time):
    ## let's first quickly define the boolean series against which we will filter our data to get the price/instrument name
    date_trade = df_options.iloc[0]["date"].date()
    nearest_expiry = df_options.iloc[0]["nearest_expiry"]
    time_filter = df_options["_timestamp"] == str(df_options.iloc[0]["date"].date())+ " " + entry_time
    tag_filter = df_options["Tag"] == "ATM"
    option_type_filter_ce = df_options["Option Type"] == "CE"
    option_type_filter_pe = df_options["Option Type"] == "PE"
    ##Below we define the expiry filter basically if we are trading on the expiry day, then we will pick the instrument from next expiry, else from the same expiry
    expiry_filter = (df_options["Expiry"] == df_options["nearest_expiry"].astype(str) 
                 if date_trade < nearest_expiry 
                 else df_options["Expiry"] == df_options["next_nearest_expiry"].astype(str))
    ##Now let's update our dict_signal dictionary (we will check if data is actually there i.e. there is an instrument which satisfies all the filters)
    if signal == "CE":
        filtered = df_options[time_filter & tag_filter & option_type_filter_ce & expiry_filter]  # ADDED
        if len(filtered) > 0:  # ADDED
            instrument = filtered["_instrumentname"].values[0]  # CHANGED: use filtered
            ##Getting the OHLC price to be passed into the execution function 
            open_price, high_price, low_price, close_price = filtered["_open"].values[0], filtered["_high"].values[0], filtered["_low"].values[0], filtered["_close"].values[0]  # CHANGED: use filtered
            if instrument:
                buy_price, buy_execution_cost = execution.txn_price_simple_avg("BUY", open_price, high_price, low_price, close_price)
                dict_signal[date_trade] = {"Instrument": instrument, "Buy Price": buy_price, "Buy Execution Cost": buy_execution_cost}
                logger.info(f"{date_trade}: BUY CE @ {buy_price:.2f}")  # ADDED
            else:
                logger.error(f"No ATM CE instrument {instrument} found for {date_trade}")  # CHANGED from print
        else:  # ADDED
            instrument = None  # ADDED
            logger.warning(f"{date_trade}: No matching CE instrument found")  # ADDED
    elif signal == "PE":
        filtered = df_options[time_filter & tag_filter & option_type_filter_pe & expiry_filter]  # ADDED
        if len(filtered) > 0:  # ADDED
            instrument = filtered["_instrumentname"].values[0]  # CHANGED: use filtered
            open_price, high_price, low_price, close_price = filtered["_open"].values[0], filtered["_high"].values[0], filtered["_low"].values[0], filtered["_close"].values[0]  # CHANGED: use filtered
            if instrument:
                buy_price, buy_execution_cost = execution.txn_price_simple_avg("BUY", open_price, high_price, low_price, close_price)
                dict_signal[date_trade] = {"Instrument": instrument, "Buy Price": buy_price , "Buy Execution Cost": buy_execution_cost} 
                logger.info(f"{date_trade}: BUY PE @ {buy_price:.2f}")  # ADDED
            else:
                logger.error(f"No ATM PE instrument {instrument} found for {date_trade}")  # CHANGED from print
        else:  # ADDED
            instrument = None  # ADDED
            logger.warning(f"{date_trade}: No matching PE instrument found") #ADDED
    else:
        instrument = None  # ADDED
        logger.error(f"Invalid signal '{signal}' for {date_trade} - must be CE or PE")  # CHANGED from print
    return dict_signal, instrument, date_trade
    
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#


"""
Signature:
    Inputs:
        df_options(Pandas df): The df on which we will operate on, should have the same fields as we defined in dict_signal_buy
        dict_signal- which will be of type {date: {"Instrument": xxxyyy, "Buy Price": 1122.3, "Sell Price": 2232,4, "Buy Execution Cost": 2.2, "Sell Execution Cost": 3.2}} and will be updated for each day
            For this specific function we will update the sell price
        exit_time (String): Should be a string representing when we are looking to exit our ce/pe of the form "09:16:00" the next day
        instrumentname (String): Should be a string representing the instrument we want to exit at the exit time the next day, for e.g. NIFTY06JAN2217650CE
        date_dict (Datetime python): this will be date for which we will update our dict_signal, will be of type: datetime.date(2022, 1, 3)
    Outputs:
        Transformed dict_signal (Dict): which will have two additional key value pairs 
            ONe for the corresponding date_dict which will be "Sell Price" : 100.1
            And one for "Sell Execution Cost" as cost of execution and slippage
Purpose:
    This function will update the dict_signal dictionary which we are maintaining , with the sell price of the option we bought the previous day, and the sell execution cost
"""

def dict_signal_sell(df_options, exit_time, dict_signal, instrumentname, date_dict):
    ##Let's first define the filters against which we willl caputre our prices to be updated
    date_trade = df_options.iloc[0]["date"].date()
    time_filter = df_options["_timestamp"] == str(date_trade) + " " + exit_time
    instrument_filter = df_options["_instrumentname"] == instrumentname
    
    # Filter first, check if data exists
    filtered = df_options[time_filter & instrument_filter]
    
    if date_dict not in dict_signal:  # ADDED
        return dict_signal  # ADDED
    
    if len(filtered) > 0:
        open_price, high_price, low_price, close_price = filtered["_open"].values[0], filtered["_high"].values[0], filtered["_low"].values[0], filtered["_close"].values[0]
        sell_price, sell_execution_cost = execution.txn_price_simple_avg("SELL",open_price, high_price, low_price, close_price)
        dict_signal[date_dict]["Sell Price"] = sell_price
        dict_signal[date_dict]["Sell Execution Cost"] = sell_execution_cost
        logger.info(f"{date_trade}: SELL {instrumentname} @ {sell_price:.2f}")  # ADDED
    else:
        dict_signal[date_dict]["Sell Price"] = None 
        logger.error(f"Exit failed for {instrumentname} on {date_trade}, pls discard this row")  # CHANGED from print
    return dict_signal
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

"""
Signature:
    Inputs:
        list_df (List of Dataframes): The df on which we will operate on, should have the same fields as we defined in dict_signal_buy
        dict_signal
        dict_signal (Dictioary):  which will be of type {date: {"Instrument": xxxyyy, "Buy Price": 1122.3, "Sell Price": 2232,4, "Buy Execution Cost": 2.2, "Sell Execution Cost": 3.2}} and will be updated for each day
        morning_time/evening_time (String): This is the morning time to process our spot price logic through functino get_entry_exit_spot, should be of type "09:15:00"
        option_entry_time/option_exit_time (String): While this could be same as morning/evening time, this is actually the entry and exit time of our option which we bought and sold the next day
        date_dict (Datetime Python): The date which will be passed as argument to the dict_signal_sell function which we defined above (basically the previous date on which we bough the option) - should be of type datetime.date(2022, 1, 3)
            Will be initialised to None and will be modified to the value as defined by calling the function dict_signal_buy
        instrumentname(String) : The name of instrument which we bought on the previous day
            Will be initialised to None and will be modified to the value as defined by calling the function dict_signal_buy
        counter (Int): Just a counter to help us with running recursion, initialised to 0
    Output:
        dict_signal (Dictioary): Will be returned with date, Instrument, buy and sell price for each date
Purpose:
    To loop over a list of dataframes, check if evening price is higher than morning price, if yes, then buy call (else put) at 320, and exit the next day at 916
    Will return a dictionary with different values of dates and corresponding buy and sell prices
"""

def update_dict_signal(list_df, dict_signal, morning_time, evening_time, option_entry_time, option_exit_time, date_dict, instrumentname, counter):
    if counter == len(list_df):
        return dict_signal
    else:
        df_temp = list_df[counter]
        date_temp = str(df_temp.iloc[0]["date"])
        df_temp.head(1)
        ##Let's first get the morning and evening price of spot to generate the signal
        morning_price, evening_price = get_entry_exit_spot(df_temp, morning_time, evening_time, date_temp)
        
        if morning_price is None or evening_price is None:  # ADDED
            logger.warning(f"Skipping {date_temp} - spot price not found")  # CHANGED from print
            print(f"Skipping {date_temp} - spot price not found")  # ADDED
            counter += 1  # ADDED
            return update_dict_signal(list_df, dict_signal, morning_time, evening_time, option_entry_time, option_exit_time, None, None, counter)  # ADDED
        
        ##Now let's add the buy price of CE or PE based on the signal
        if evening_price > morning_price:
            dict_signal, instrument, date_trade = dict_signal_buy(df_temp, dict_signal, "CE", option_entry_time)
        else:
            dict_signal, instrument, date_trade = dict_signal_buy(df_temp, dict_signal, "PE", option_entry_time)
        ##Now let's add the sell price based on the instrument name and the date_dict, and then unpack the tuple for dict, instrument, and date
        if instrumentname is not None and date_dict is not None:
            dict_signal = dict_signal_sell(df_temp, option_exit_time, dict_signal, instrumentname, date_dict)
        ##And not let's call the function recursively, but lets first udpate counter and identify which date and instrument we want to pass
        counter += 1
        return update_dict_signal(list_df, dict_signal, morning_time, evening_time, option_entry_time, option_exit_time, date_trade, instrument, counter)
        

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

"""
Signature:
    Inputs:
        dict_sigal (Dictionary): which was the output from the function update_dict_signal of type {date: {"Instrument": xxxyyy, "Buy Price": 1122.3, "Sell Price": 2232,4, "Buy Execution Cost": 2.2, "Sell Execution Cost": 3.2}}
    Outputs:
        Will be a new Pandas df called df_trial, which will have the following fields:
            date (Python date): of the form datetime.date(2022, 1, 3)
            gross_pct (float): determined using (open_buy_price - open_sell_price)/(open_buy_price)
            execution_pct (float): determined using (execution_buy_price - execution_sell_price)/(execution_buy_price)
            net_pct (float): Should ideally adjust execution_pct based on STT and GST etc, but for now we are SKIPPING IT
Purpose:
    To transform the given input of dict_signal which is of type: {date: {"Instrument": xxxyyy, "Buy Price": 1122.3, "Sell Price": 2232,4, "Buy Execution Cost": 2.2, "Sell Execution Cost": 3.2}}
    into a Pandas dataframe df which will have the columns (date, gross_pct, execution_pct, net_pct)
    FOr open price on buy side we will use : buy_execution_price + buy_execution_cost, and for open price on sell side we will use sell_execution_price - sell_execution_cost

"""

def results_df(dict_signal):
    ##We will first create a new empty DF, and then will loop over the dict_signal to add each row into the df
    df_trial = pd.DataFrame(columns = ["Date", "Instrument", "Buy Price", "Buy Execution Cost", "Sell Price", "Sell Execution Cost"])
    for key, value in dict_signal.items():
        new_row = {"Date": key, "Instrument": value.get("Instrument"), "Buy Price": value.get("Buy Price"), "Buy Execution Cost": value.get("Buy Execution Cost"), "Sell Price": value.get("Sell Price"), "Sell Execution Cost": value.get("Sell Execution Cost")}
        df_trial = pd.concat([df_trial, pd.DataFrame([new_row])], ignore_index = True)
    
    ##Filter out incomplete trades (where Sell Price is None)  # ADDED
    initial_rows = len(df_trial)  # ADDED
    df_trial = df_trial[df_trial["Sell Price"].notna()]  # ADDED
    filtered_rows = initial_rows - len(df_trial)  # ADDED
    if filtered_rows > 0:  # ADDED
        logger.warning(f"Filtered {filtered_rows} incomplete trades (no exit)")  # CHANGED from print
        
    ##Now let's add pct columns and drop unnecessary columns and reorder:
    df_trial["execution_pct"] = (df_trial["Sell Price"] - df_trial["Buy Price"])/df_trial["Buy Price"]
    df_trial["gross_pct"] = (df_trial["Sell Price"] - df_trial["Sell Execution Cost"] - df_trial["Buy Price"] - df_trial["Buy Execution Cost"])/(df_trial["Buy Price"] + df_trial["Buy Execution Cost"])
    df_trial["net_pct"] = df_trial["execution_pct"]
    df_trial.rename(columns={"Date": "date"}, inplace=True)
    df_trial.drop(columns = ["Instrument", "Buy Price", "Buy Execution Cost", "Sell Price", "Sell Execution Cost"], inplace = True)
    df_trial = df_trial[["date", "gross_pct", "execution_pct", "net_pct"]]
    return df_trial


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
"""
Signature:
    Inputs: 
        df_results (Pandas DF): A pandas df which will be the result of the previous function results_df, and should have the following columns"
            date (Python date): of the form datetime.date(2022, 1, 3)
            gross_pct (float): determined using (open_buy_price - open_sell_price)/(open_buy_price)
            execution_pct (float): determined using (execution_buy_price - execution_sell_price)/(execution_buy_price)
            net_pct (float): Should ideally adjust execution_pct based on STT and GST etc, but for now we are SKIPPING IT

        onitial_capital (Float): The initial capital with which we started the trading
        rpt (float): represents % of initial capital which we will risk per day (Acronym for risk per trade)
    Outputs:
        df_results (Pandas DF): Transformed input DF, with the following fields:
            date (Python date): of the form datetime.date(2022, 1, 3)
            gross_pnl (Float) - representing Pnl pre slippage, pre txn charges
            execution_pnl (Float) - representing gross PnL minus the slippage, pre txn charges
            net_pnl (Float) - representing net PnL , net of slippage, net of txn charges
        results.csv(CSV file) - in the same folder in which we are running the code
Purpose: To transform input pandas df by adding the actual pnl bassed on the initial capittal and defined rpt , we will also drop _pct columns to keep things simple and readable 
"""

def results_final(df_results, initial_capital, rpt):
    ##Fairly easy just adding some new columns and dropping original columns
    risk_per_trade = rpt*initial_capital
    df_results["gross_pnl"] = df_results["gross_pct"]*risk_per_trade
    df_results["execution_pnl"] = df_results["execution_pct"]*risk_per_trade
    df_results["net_pnl"] = df_results["net_pct"]*risk_per_trade
    df_results.drop(columns = ["gross_pct", "execution_pct", "net_pct"], inplace = True)    
    df_results.to_csv("results.csv", index=False, header=True, sep=",", encoding='utf-8' )
    return df_results