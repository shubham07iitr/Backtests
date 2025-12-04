##Importing the relevant libraries/packages
import pandas as pd
import re ##regex
import os
import numpy as np
from functools import reduce ##reduce will help us club multiple filters together
import operator

"""
Type/Interpretation - Execution is a collection of methods to model different txns with certain slippage assumptions 
It will have 1 attributes for itself:
- slippage_pct(float): In % terms, how much slippage we want to assum diring exection, for e.g. 0.02 will represent 2% slippage
"""
class Execution():
    def __init__(self, slippage_pct = 0.01):
            self.slippage_pct = slippage_pct
    
    """
    TEMPLATE
    -- FIELDS (NONE)
    .....self.slippage_pct    .....FLOAT

    -- METHODS:
    .....self.txn_price_simple_avg(self, signal (STRING)): .... (execution_price, execution_cost) BOTH FLOATS
    """

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    """
    Signature:
        Inputs:
            signal (String): Should be either "BUY" or "SELL"
            open(float): Open price of the candle for which we want to txn at, such as 123.2
            high(float): Open price of the candle for which we want to txn at, such as 123.2
            low(float): Open price of the candle for which we want to txn at, such as 123.2
            close(float): Open price of the candle for which we want to txn at, such as 123.2
            
        Outputs:
            exectution_price(float): Will be the simple avg of OHLC data + some % slippage modeled
            execution_cost(float): negative means we are losging, positive means we are actually winning or benefiting
                Will be open price - execution price for buy signal, 
                execution price - open price for sell signal
    Purpose: 
        To capture the execution price in an actual txn using simple avg of OHLC proce*% of slippage modeled 
        For e.g. avg(1,2,3,4)*(1+0.02) for buy, and avg(1,2,3,4)*(1-0.02) for sell
    """
    
    def txn_price_simple_avg(self, signal, open_price, high_price, low_price, close_price):
            
            if signal == "BUY":
                execution_price = (sum([open_price, high_price, low_price, close_price])/4)*(1+self.slippage_pct) 
                execution_cost = open_price - execution_price
            elif signal == "SELL":
                execution_price = (sum([open_price, high_price, low_price, close_price])/4)*(1-self.slippage_pct) 
                execution_cost = execution_price - open_price
            else:
                raise ValueError(f"Invalid signal: '{signal}'. Must be 'BUY' or 'SELL'")  # ADDED
            return execution_price, execution_cost

              
        
                

                