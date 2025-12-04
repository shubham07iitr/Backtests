##Importing the relevant libraries/packages
from datetime import datetime
import pandas as pd
import re ##regex
import os
import numpy as np
from functools import reduce ##reduce will help us club multiple filters together
import operator
import matplotlib.pyplot as plt
##Following imports are for generating the nice pdf report
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

##Setting up the logger
import logging
logger = logging.getLogger(__name__)


"""
Type/Interpretation:
    Metrics class is a collection of methods to operate on loading the files for running backtests
    It is of compound datatype
    - df_results (PANDAS DF) which will be passed on during initialisation
        The dataframe should have 4 columns:
            date (Python Datetime) - representing the day of the trade , for e.g. datetime.date(2022, 1, 3)
            gross_pnl (Float) - representing Pnl pre slippage, pre txn charges
            execution_pnl (Float) - representing gross PnL minus the slippage, pre txn charges
            net_pnl (Float) - representing net PnL , net of slippage, net of txn charges
        Other than these 4 columns the df could have more columns but we wouldnt care about those
    - initial_capital(Float) - inital capital with which we will be playing
    
"""

class Metrics():
    def __init__(self, df_results, initial_capital):
        if initial_capital == 0:
            raise ValueError("Initial capital cannot be 0")
        else:
            self.df_results = df_results
            self.initial_capital = initial_capital
    
    """
    TEMPLATE
    -- FIELDS 
        ...self.df_results ....Pandas DF
        ...self.initial_capital ....Float
    -- METHODS
        RETURNS MEASURE
        ...self.total_return_pct(self)     ......(gross_return_pct, execution_return_pct, net_return_pct) ALL FLOATS
        ...self.cagr_return_pct(self)           ......(gross_cagr_pct, execution_cagr_pct, net_cagr_pct) ALL FLOATS
        ...self.distributed_returns_df(self)     ......styled_df (PANDAS DF)
        RISK MEASURE
        ...self.max_drawdown_pct(self)           ......(gross_max_dd_pct, execution_max_dd_pct, net_max_dd_pct) ALL FLOATS
        ....self.calmar_ratio(self)             ......(gross_calmar, execution_calmar, net_calmar) ALL FLOATS
        ....self.sharpe_ratio(self, annual_risk_free_rate (FLOAT))             ......(gross_sharpe_annual, execution_sharpe_annual, net_sharpe_annual) ALL_FLOATS
        ....self.sortino_ratio(self, target_return (FLOAT))         ........(gross_sortino_annual, execution_sortino_annual, net_sortino_annual) ALL FLOATS
        ....self.max_drawdown_duration_days(self)               ......(gross_dd_days, execution_dd_days, net_dd_days) ALL FLOATS
        WIN/LOSS MEASURE
        ....self.total_trades(Self)           ......total_traded(INT)
        ....self.winrate_pct(self)            ......(gross_winrate_pct, execution_winrate_pct, net_winrate_pct) ALL FLOATS
        ....self.largest_win_pct(self)        ......(gross_largest_win_pct, execution_largest_win_pct, net_largest_win_pct) ALL FLOATS
        ....self.largest_loss_pct(self)       ......(gross_largest_loss_pct, execution_largest_loss_pct, net_largest_loss_pct) ALL FLOATS
        ....self.avg_win_pct(self)            ......(gross_avg_win_pct, execution_avg_win_pct, net_avg_win_pct) ALL FLOATS
        ....self.avg_loss_pct(self)           ......(gross_avg_loss_pct, execution_avg_loss_pct, net_avg_loss_pct) ALL FLOATS
        ....self.expectancy.pct(self)         ......(gross_expectancy_pct, execution_expectancy_pct, net_expectancy_pct) ALL FLOATS
        PLOTS
        .....self.generate_equity_curve(self, gross(BOOLEAN), execution(BOOLEAN), net(BOOLEAN), filename(STRING)): ......filename (String) (Will also generate a png file and save in the same folder)
        .....self.generate_dd_curve(self, gross(BOOLEAN), execution(BOOLEAN), net(BOOLEAN), filename(STRING))     ......filename (String) (Will also generate a png file and save in the same folder)
        .....self.combine_equity_dd_curve(self, gross(BOOLEAN), execution(BOOLEAN), net(BOOLEAN), filename(STRING))     ......filename (String) (Will also generate a png file and save in the same folder)
        ....self.generate_report(self, strategy (STRING), return_type(STRING), logic(STRING), filename(STRING)):        ......filename (String) (Will also generate a png file and save in the same folder)


    """

    #---------------------------------------------------------------RETURNS MEASURE-------------------------------------------------------------------------------------------------------------------------------------#

    """
    Signature:
        Inputs: self
        Outputs: Will be a three way tuple as below:
            gross_return_pct (Float): commensurate to the gross PnL
            execution_return_pct (Float): commensurate to execution_pnl
            net_return_pct (Float) : commensurate to net_pnl
    Purpose: To generate cumulative return pct (gross, execution, net) for the objct created
    """
    def total_return_pct(self):
        gross_return_pct = self.df_results["gross_pnl"].sum()/self.initial_capital
        execution_return_pct = self.df_results["execution_pnl"].sum()/self.initial_capital
        net_return_pct = self.df_results["net_pnl"].sum()/self.initial_capital
        return gross_return_pct, execution_return_pct, net_return_pct
    


    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_cagr_pct (Float): commensurate to the gross PnL
            execution_cagr_pct (Float): commensurate to execution_pnl
            net_cagr_pct (Float) : commensurate to net_pnl
    Purpose: To generage CAGR return pct (gross, execution, net) for the object created
        Formula for CAGR - (Ending Value / Beginning Value)^(1/Years) - 1 where years = (end date - begin date)/365.25
    """
    def cagr_return_pct(self):
        time_period = self.df_results.date.max() - self.df_results.date.min()
        years = time_period.days/365.25
        gross_final_value = self.initial_capital +  self.df_results["gross_pnl"].sum()
        execution_final_value = self.initial_capital +  self.df_results["execution_pnl"].sum()
        net_final_value = self.initial_capital +  self.df_results["net_pnl"].sum()
        gross_cagr_pct = ((gross_final_value/self.initial_capital)**(1/years)) - 1
        execution_cagr_pct = ((execution_final_value/self.initial_capital)**(1/years)) - 1 
        net_cagr_pct = ((net_final_value/self.initial_capital)**(1/years)) - 1 
        return gross_cagr_pct, execution_cagr_pct, net_cagr_pct
    

    """
    Signature:
        Inputs:
            self
            return_type (String) : Should be one of "gross", "execution", "net" - will be used to generate the pnl accoordingly
        Outputs:
            distributed_returns_df (Pandas df) : 
                this will have 13 rows (or index), 1 each for every month , and one for total
                n+1 number of columns where every column represents 1 year, and final column as total
                Each cell will represent return for that month/year combination and will be of type float
    Purpose:
        To generate a distributed table for return % across month/year cuts , each row represented as an index willl represent a month, and each column will represent anyear

    """
    def distributed_returns_df(self, return_type):
        """
        Generate monthly/yearly distributed returns table with conditional formatting
        """
            # Select the appropriate return column
        if return_type == "gross":
            return_col = "gross_pnl"
        elif return_type == "execution":
            return_col = "execution_pnl"
        elif return_type == "net":
            return_col = "net_pnl"
        else:
            raise ValueError("return_type must be 'gross', 'execution', or 'net'")
        
        # Create working dataframe
        df_work = self.df_results[['date', return_col]].copy()
        df_work['date'] = pd.to_datetime(df_work['date'])
        df_work['year'] = df_work['date'].dt.year
        df_work['month'] = df_work['date'].dt.month
        
        # Convert PnL to percentage and aggregate
        df_work['return_pct'] = df_work[return_col] / self.initial_capital * 100
        monthly_returns = df_work.groupby(['year', 'month'])['return_pct'].sum()
        
        # Pivot to create the matrix (months as rows, years as columns)
        pivot_table = monthly_returns.reset_index().pivot(index='month', columns='year', values='return_pct')
        
        # Add row totals (sum across years for each month)
        pivot_table['Total'] = pivot_table.sum(axis=1)
        
        # Add column totals (sum down months for each year)
        yearly_totals = pivot_table.sum(axis=0)
        pivot_table.loc['Total'] = yearly_totals
        
        # Rename index for clarity
        month_names = {1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 
                    7: '7', 8: '8', 9: '9', 10: '10', 11: '11', 12: '12', 'Total': 'Total'}
        pivot_table.index = pivot_table.index.map(lambda x: month_names.get(x, str(x)))
        
        # Apply conditional formatting
        def color_scale(val):
            if pd.isna(val):
                return 'background-color: white'
            elif val < -1.5:
                return 'background-color: #ff9999; color: black'
            elif val < -0.5:
                return 'background-color: #ffcc99; color: black'
            elif val < 0.5:
                return 'background-color: #ffff99; color: black'
            elif val < 2.0:
                return 'background-color: #ccff99; color: black'
            elif val < 4.0:
                return 'background-color: #99ff99; color: black'
            else:
                return 'background-color: #66ff66; color: black'
        
        styled_df = pivot_table.style.applymap(color_scale).format('{:.1f}', na_rep='-')
        
        return styled_df
    
    
    #----------------------------------------------------------------------RISK MEASURE---------------------------------------------------------------------------------------------------------------------------------#
    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_max_dd_pct (Float): commensurate to the gross PnL
            execution_max_dd_pct (Float): commensurate to execution_pnl
            net_max_dd_pct (Float) : commensurate to net_pnl
    Purpose: To generage max DD pct (gross, execution, net) for the object created
        Formula for max DD - Max(Peak Value - Trough Value) / Peak Value
        Steps to follow:
            Calculate cumulative equity curve
            Calculate running maximum (peak)
            Calculate drawdown at each point = (Current Value - Peak) / Peak
            Maximum Drawdown = Most negative drawdown value
        Here return values be of type -0.15 which means the max DD over the period is 15% 
    """
     
    def max_drawdown_pct(self):
        # Create equity curves, the below variables are series, cumsum gets the cumsum series
        gross_equity = self.initial_capital + self.df_results["gross_pnl"].cumsum()
        execution_equity = self.initial_capital + self.df_results["execution_pnl"].cumsum()
        net_equity = self.initial_capital + self.df_results["net_pnl"].cumsum()
        
        # Calculate running maximum (peak), also series the below vairables
        gross_peak = gross_equity.cummax()
        execution_peak = execution_equity.cummax()
        net_peak = net_equity.cummax()
        
        # Calculate drawdown at each point, also series, the below vars
        gross_drawdown = (gross_equity - gross_peak) / gross_peak
        execution_drawdown = (execution_equity - execution_peak) / execution_peak
        net_drawdown = (net_equity - net_peak) / net_peak
        
        # Maximum drawdown is the minimum (most negative) value
        gross_max_dd_pct = gross_drawdown.min()
        execution_max_dd_pct = execution_drawdown.min()
        net_max_dd_pct = net_drawdown.min()
        
        return gross_max_dd_pct, execution_max_dd_pct, net_max_dd_pct
    

    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_calmar(Float): commensurate to the gross PnL
            execution_calmar (Float): commensurate to execution_pnl
            net_calmar (Float) : commensurate to net_pnl
    Purpose: To generage calmar ratio (3 way - gross, execution, net) for the object created
        Formula for calmar: cagr/max dd
        We will abs for max DD as max DD will return negative values for us
    """
    def calmar_ratio(self):
        gross_calmar = self.cagr_return_pct()[0]/abs(self.max_drawdown_pct()[0])
        execution_calmar = self.cagr_return_pct()[1]/abs(self.max_drawdown_pct()[1])
        net_calmar = self.cagr_return_pct()[2]/abs(self.max_drawdown_pct()[2])
        return gross_calmar, execution_calmar, net_calmar
    

    """
    Signature:
        Inputs:
            Self
            annual_risk_free_rate (float) : Would be the risk free rate which is the opportunity cost for us, will be defaulted to 0, but usually for India it would be ~5-6% annual
        Outputs: Will be a 3 way tuple as below:
            gross_sharpe_annual(Float): commensurate to the gross PnL
            execution_sharpe_annual (Float): commensurate to execution_pnl
            net_sharpe_annual (Float) : commensurate to net_pnl
    Purpose: To generate annualised sharpe ratio (3 way - gross, execution, net) for the object created
        Formual for sharpe:  (Mean Return per period - risk free rate per period/ Std Dev) × √(Periods per Year)
    """

    def sharpe_ratio(self, annual_risk_free_rate = 0):
      # Calculate time period and trades per year
        time_period_years = (self.df_results.date.max() - self.df_results.date.min()).days / 365.25
        total_trades = self.total_trades()
        trades_per_year = total_trades / time_period_years
        
        # Convert annual risk-free rate to per-trade rate
        risk_free_per_trade = annual_risk_free_rate / trades_per_year if annual_risk_free_rate != 0 else 0
        
        # Calculate returns per trade
        gross_returns = self.df_results["gross_pnl"] / self.initial_capital
        execution_returns = self.df_results["execution_pnl"] / self.initial_capital
        net_returns = self.df_results["net_pnl"] / self.initial_capital
        
        # Calculate Sharpe (per trade, with excess return)
        gross_sharpe = (gross_returns.mean() - risk_free_per_trade) / gross_returns.std()
        execution_sharpe = (execution_returns.mean() - risk_free_per_trade) / execution_returns.std()
        net_sharpe = (net_returns.mean() - risk_free_per_trade) / net_returns.std()
        
        # Annualize by multiplying by sqrt(trades_per_year)
        gross_sharpe_annual = gross_sharpe * np.sqrt(trades_per_year)
        execution_sharpe_annual = execution_sharpe * np.sqrt(trades_per_year)
        net_sharpe_annual = net_sharpe * np.sqrt(trades_per_year)
        
        return gross_sharpe_annual, execution_sharpe_annual, net_sharpe_annual


    """
    Signature:
        Inputs:
            Self
            annual_target_return (float) : of type 0.15 etc where this is the expected return for the year, will be defauled to 0
        Outputs: Will be a 3 way tuple as below:
            gross_sortino_annual (Float): commensurate to the gross PnL
            execution_sortino_annual (Float): commensurate to execution_pnl
            net_sortino_annual (Float) : commensurate to net_pnl
    Purpose:
        To compute 3 way sortino (for gross, execution, net)
        Sortino is like Sharpe, but ONLY penalizes downside volatility (losses), not upside volatility (gains).
            Sortino Ratio = (Mean Return - Target Return) / Downside Deviation
    """

    def sortino_ratio(self, target_return = 0):
        # Calculate time period and trades per year
        time_period_years = (self.df_results.date.max() - self.df_results.date.min()).days / 365.25
        total_trades = len(self.df_results)
        trades_per_year = total_trades / time_period_years
        
        # Calculate returns per trade
        gross_returns = self.df_results["gross_pnl"] / self.initial_capital
        execution_returns = self.df_results["execution_pnl"] / self.initial_capital
        net_returns = self.df_results["net_pnl"] / self.initial_capital
        
        # Calculate downside deviation (only negative returns)
        gross_downside = gross_returns[gross_returns < target_return]
        execution_downside = execution_returns[execution_returns < target_return]
        net_downside = net_returns[net_returns < target_return]
        
        gross_downside_std = gross_downside.std()
        execution_downside_std = execution_downside.std()
        net_downside_std = net_downside.std()
        
        # Calculate Sortino (per trade)
        gross_sortino = (gross_returns.mean() - target_return) / gross_downside_std
        execution_sortino = (execution_returns.mean() - target_return) / execution_downside_std
        net_sortino = (net_returns.mean() - target_return) / net_downside_std
        
        # Annualize
        gross_sortino_annual = gross_sortino * np.sqrt(trades_per_year)
        execution_sortino_annual = execution_sortino * np.sqrt(trades_per_year)
        net_sortino_annual = net_sortino * np.sqrt(trades_per_year)
        
        return gross_sortino_annual, execution_sortino_annual, net_sortino_annual
    
    """
    Signature:
        Inputs:
            Self
        Outputs: Will be a 3 way tuple as below:
            gross_dd_days (Float): commensurate to the gross PnL
            execution_dd_days (Float): commensurate to execution_pnl
            net_dd_days (Float) : commensurate to net_pnl
    Purpose:
        To compute 3 way max days in DD (for gross, execution, net)
        We will use a helper function here which will compute the dd_duration for a series, and then use it to operate on different pnls
    """
    def max_drawdown_duration_days(self):

        ##Defining a helper function     
        def calc_max_dd_duration(equity_series, dates):
            # Calculate peak
            peak = equity_series.cummax()
            # Create drawdown indicator
            in_dd = (equity_series < peak).astype(int)
            # Create groups for consecutive drawdowns
            dd_groups = (in_dd != in_dd.shift()).cumsum()
            # Filter only drawdown periods
            dd_periods = pd.DataFrame({
                'date': dates,
                'in_dd': in_dd,
                'group': dd_groups
            })
            dd_periods = dd_periods[dd_periods['in_dd'] == 1]
            if len(dd_periods) == 0:
                return 0
            # Calculate duration for each group
            durations = dd_periods.groupby('group')['date'].agg(
                lambda x: (x.max() - x.min()).days
            )
            return durations.max() if len(durations) > 0 else 0
        
        # Calculate equity curves
        gross_equity = self.initial_capital + self.df_results["gross_pnl"].cumsum()
        execution_equity = self.initial_capital + self.df_results["execution_pnl"].cumsum()
        net_equity = self.initial_capital + self.df_results["net_pnl"].cumsum()
        
        dates = self.df_results['date']
        
        gross_dd_days = calc_max_dd_duration(gross_equity, dates)
        execution_dd_days = calc_max_dd_duration(execution_equity, dates)
        net_dd_days = calc_max_dd_duration(net_equity, dates)
        
        return gross_dd_days, execution_dd_days, net_dd_days

    #----------------------------------------------------------------------WIN/LOSS MEASURE-----------------------------------------------------------------------------------------------------------------------------#
    """
    Signature:
        Inputs: Self
        Outputs: total_trades (Int)
    Purpose - To get the total trades taken in the strat, where pnl is not none
    """
    def total_trades(self):
        return self.df_results.gross_pnl.count()
    

    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_winrate_pct (Float): commensurate to the gross PnL
            execution_winrate_pct (Float): commensurate to execution_pnl
            net_winrate_pct (Float) : commensurate to net_pnl
    Purpose: To generage winrate (winning trades/total trades) return pct (gross, execution, net) for the object created
        We will skip any day where PnL is None
    """
    def winrate_pct(self):
        gross_winrate_pct = len(self.df_results[self.df_results["gross_pnl"] > 0])/self.total_trades()  # ✅ Add len()
        execution_winrate_pct = len(self.df_results[self.df_results["execution_pnl"] > 0])/self.total_trades()  # ✅ Add len()
        net_winrate_pct = len(self.df_results[self.df_results["net_pnl"] > 0])/self.total_trades()  # ✅ Add len()
        return gross_winrate_pct, execution_winrate_pct, net_winrate_pct

    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_largest_win_pct (Float): commensurate to the gross PnL 
            execution_largest_win_pct (Float): commensurate to execution_pnl 
            net_largest_win_pct (Float) : commensurate to net_pnl 
    Purpose: To generage largest win_pct for a single day for the 3 different pnl we have, winPct defined as pnl for the day/initial_capital
        We will skip any day where PnL is None
    """
    def largest_win_pct(self):
        gross_largest_win_pct = self.df_results.gross_pnl.max()/self.initial_capital
        execution_largest_win_pct = self.df_results.execution_pnl.max()/self.initial_capital
        net_largest_win_pct = self.df_results.net_pnl.max() /self.initial_capital
        return gross_largest_win_pct, execution_largest_win_pct, net_largest_win_pct
    

    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_largest_loss_pct (Float): commensurate to the gross PnL 
            execution_largest_loss_pct (Float): commensurate to execution_pnl 
            net_largest_loss_pct (Float) : commensurate to net_pnl 
    Purpose: To generage largest loss_pct for a single day for the 3 different pnl we have, loss_pct defined as pnl for the day/initial_capital
        We will skip any day where PnL is None
    """
    def largest_loss_pct(self):
        gross_largest_loss_pct = self.df_results.gross_pnl.min()/self.initial_capital
        execution_largest_loss_pct = self.df_results.execution_pnl.min()/self.initial_capital
        net_largest_loss_pct = self.df_results.net_pnl.min()/self.initial_capital
        return gross_largest_loss_pct, execution_largest_loss_pct, net_largest_loss_pct
    
    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_avg_win_pct (Float): commensurate to the gross PnL 
            execution_avg_win_pct (Float): commensurate to execution_pnl 
            net_avg_win_pct (Float) : commensurate to net_pnl 
    Purpose: To generage avg_win_pct for a single day for the 3 different pnl we have
        We will skip any day where PnL is None
        Avg_win_pct is defined as (total win pnl/total winning trades)/initial capital
    """
    def avg_win_pct(self):
        # Use .mean() directly - it's cleaner
        gross_avg_win = self.df_results[self.df_results["gross_pnl"] > 0]["gross_pnl"].mean()
        execution_avg_win = self.df_results[self.df_results["execution_pnl"] > 0]["execution_pnl"].mean()
        net_avg_win = self.df_results[self.df_results["net_pnl"] > 0]["net_pnl"].mean()
        
        # Convert to percentage of capital
        gross_avg_win_pct = gross_avg_win / self.initial_capital
        execution_avg_win_pct = execution_avg_win / self.initial_capital
        net_avg_win_pct = net_avg_win / self.initial_capital
        
        return gross_avg_win_pct, execution_avg_win_pct, net_avg_win_pct
    
    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_avg_loss_pct (Float): commensurate to the gross PnL 
            execution_avg_loss_win_pct (Float): commensurate to execution_pnl 
            net_avg_loss_pct (Float) : commensurate to net_pnl 
    Purpose: To generage avg_loss_pct for a single day for the 3 different pnl we have
        We will skip any day where PnL is None
        Avg_loss_pct is defined as (total loss pnl/total losing trades )/initial capital
    """
    def avg_loss_pct(self):
        # Use .mean() directly - it's cleaner
        gross_avg_loss = self.df_results[self.df_results["gross_pnl"] <= 0]["gross_pnl"].mean()
        execution_avg_loss = self.df_results[self.df_results["execution_pnl"] <= 0]["execution_pnl"].mean()
        net_avg_loss = self.df_results[self.df_results["net_pnl"] <= 0]["net_pnl"].mean()
        
        # Convert to percentage of capital
        gross_avg_loss_pct = gross_avg_loss / self.initial_capital
        execution_avg_loss_pct = execution_avg_loss / self.initial_capital
        net_avg_loss_pct = net_avg_loss / self.initial_capital
        
        return gross_avg_loss_pct, execution_avg_loss_pct, net_avg_loss_pct

    """
    Signature:
        Inputs: self
        Outputs: Will be a 3 way tuple as below:
            gross_expectancy (float): commensurate to the gross PnL 
            execution_expectancy (float) : commensurate to execution_pnl 
            net_expectancy (float) :commensurate to net_pnl 
    Purpose: to generate expected value or expectancy for a single day for 3 different pnl wehave
        expectancy is defined as (avg win_pct)*winrate + (avg loss_pct)*lossrate
    """
    def expectancy_pct(self):
        gross_expectancy_pct = self.avg_win_pct()[0]* self.avg_win_pct()[0] + self.avg_loss_pct()[0]* self.avg_loss_pct()[0]
        execution_expectancy_pct = self.avg_win_pct()[1]* self.avg_win_pct()[1] + self.avg_loss_pct()[1]* self.avg_loss_pct()[1]
        net_expectancy_pct = self.avg_win_pct()[1]* self.avg_win_pct()[1] + self.avg_loss_pct()[1]* self.avg_loss_pct()[1]
        return gross_expectancy_pct, execution_expectancy_pct, net_expectancy_pct
    
        

    
    #----------------------------------------------------------------------PLOTS-----------------------------------------------------------------------------------------------------------------------------#
    """
    Signature:
        Inputs:
            self
            gross (Boolean) - whether we want to map gross_equity_curve (default to be false)
            execution (Boolean) - whether we want to map execution_equity_curve (default to be false)
            net (Boolean) - whether we want to map net_equity_curve (default to be false)
            filename (Stirng) - optional argument with default valye as equity_curve.png , will be useful for code reusability
        Outputs:
            Plot of equity curve vs time (PNG) - saved directly in the same folder in which we are using the function
                Each of the curves (gross, execution, net) to be mapped on same curve with different colors and use of legends
                Legend should also mention the cagr return for each of the curve mapped
            filename - returns the filename of the file which was generated (png in this case) - this is just useful to make code more reusable, in case we want to use the file generated for some other function
    Purpose:
        Generate the equity curve based on initial capital and returns form start date till end date, and save as PnG in the same folder, also returns the filename which was created
    """
    def generate_equity_curve(self, gross=False, execution=False, net=False, filename="equity_curve.png"):
        """
        Generate equity curve plot with CAGR in legend
        """
        plt.figure(figsize=(14, 7))
        
        # Get CAGR values
        gross_cagr, execution_cagr, net_cagr = self.cagr_return_pct()
        
        if gross:
            gross_equity = self.initial_capital + self.df_results["gross_pnl"].cumsum()
            plt.plot(self.df_results['date'], gross_equity, label=f'Gross (CAGR: {gross_cagr:.2%})', 
                    linewidth=2, color='blue')
        
        if execution:
            execution_equity = self.initial_capital + self.df_results["execution_pnl"].cumsum()
            plt.plot(self.df_results['date'], execution_equity, label=f'Execution (CAGR: {execution_cagr:.2%})', 
                    linewidth=2, color='green')
        
        if net:
            net_equity = self.initial_capital + self.df_results["net_pnl"].cumsum()
            plt.plot(self.df_results['date'], net_equity, label=f'Net (CAGR: {net_cagr:.2%})', 
                    linewidth=2, color='orange')
        
        plt.title('Equity Curve', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Portfolio Value', fontsize=12)
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved equity curve: {filename}")
        return filename  # ADDED


    """
    Signature:
        Inputs:
            self
            gross (Boolean) - whether we want to map gross_dd_curve (default to be false)
            execution (Boolean) - whether we want to map execution_dd_curve (default to be false)
            net (Boolean) - whether we want to map net_dd_curve (default to be false)
            filename (Stirng) - optional argument with default valye as drawdown_curve.png , will be useful for code reusability
        Outputs:
            Plot of DD curve vs time (PNG) - saved directly in the same folder in which we are using the function
                Each of the curves (gross, execution, net) to be mapped on same curve with different colors and use of legends
                Legend should also mention the max DD% for each of the curve mapped
            filename - returns the filename of the file which was generated (png in this case) - this is just useful to make code more reusable, in case we want to use the file generated for some other function
    Purpose:
        Generate the DD curve based on initial capital and DD from start date till end date, and save as PnG in the same folder, also returns the file name which was generated
    """
    def generate_dd_curve(self, gross=False, execution=False, net=False, filename="drawdown_curve.png"):
        """
        Generate drawdown curve plot with max DD in legend
        """
        plt.figure(figsize=(14, 7))
        
        # Get max DD values
        gross_max_dd, execution_max_dd, net_max_dd = self.max_drawdown_pct()
        
        if gross:
            gross_equity = self.initial_capital + self.df_results["gross_pnl"].cumsum()
            gross_peak = gross_equity.cummax()
            gross_dd = (gross_equity - gross_peak) / gross_peak * 100
            plt.plot(self.df_results['date'], gross_dd, label=f'Gross (Max DD: {gross_max_dd:.2%})', 
                    linewidth=2, color='blue')
        
        if execution:
            execution_equity = self.initial_capital + self.df_results["execution_pnl"].cumsum()
            execution_peak = execution_equity.cummax()
            execution_dd = (execution_equity - execution_peak) / execution_peak * 100
            plt.plot(self.df_results['date'], execution_dd, label=f'Execution (Max DD: {execution_max_dd:.2%})', 
                    linewidth=2, color='green')
        
        if net:
            net_equity = self.initial_capital + self.df_results["net_pnl"].cumsum()
            net_peak = net_equity.cummax()
            net_dd = (net_equity - net_peak) / net_peak * 100
            plt.plot(self.df_results['date'], net_dd, label=f'Net (Max DD: {net_max_dd:.2%})', 
                    linewidth=2, color='orange')
        
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        plt.title('Drawdown Curve', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Drawdown (%)', fontsize=12)
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved drawdown curve: {filename}")
        return filename  # ADDED


    """
    Signature:
        Inputs:
            self
            gross (Boolean) - whether we want to map both gross dd and equity curve together (default to be false)
            execution (Boolean) - whether we want to map both execution dd and equity curve together  (default to be false)
            net (Boolean) - whether we want to map both net dd and equity curve together (default to be false)
            filename (Stirng) - optional argument with default valye as equity_dd_combined.png , will be useful for code reusability
        Outputs:
            Plot of DD + Equity curve vs time (PNG) - saved directly in the same folder in which we are using the function
                This will just run both the equity curve function and dd curve function together , and will generate a single png file
                Top half will be equity curve, and bottom half will be the DD perfectly aligned with top half
            filename - returns the filename of the file which was generated (png in this case) - this is just useful to make code more reusable, in case we want to use the file generated for some other function
    Purpose:
        Generate the DD curve based on initial capital and DD from start date till end date, and save as PnG in the same folder, also returns the file name of the png file which was generated

    """
    def combine_equity_dd_curve(self, gross=False, execution=False, net=False, filename="equity_dd_combined.png"):
        """
        Generate combined equity + drawdown plot (2 panels aligned)
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        # Get metrics
        gross_cagr, execution_cagr, net_cagr = self.cagr_return_pct()
        gross_max_dd, execution_max_dd, net_max_dd = self.max_drawdown_pct()
        
        # Top panel - Equity Curve
        if gross:
            gross_equity = self.initial_capital + self.df_results["gross_pnl"].cumsum()
            ax1.plot(self.df_results['date'], gross_equity, label=f'Gross (CAGR: {gross_cagr:.2%})', 
                    linewidth=2, color='blue')
            
            # Bottom panel - DD for gross
            gross_peak = gross_equity.cummax()
            gross_dd = (gross_equity - gross_peak) / gross_peak * 100
            ax2.plot(self.df_results['date'], gross_dd, label=f'Gross (Max DD: {gross_max_dd:.2%})', 
                    linewidth=2, color='blue')
        
        if execution:
            execution_equity = self.initial_capital + self.df_results["execution_pnl"].cumsum()
            ax1.plot(self.df_results['date'], execution_equity, label=f'Execution (CAGR: {execution_cagr:.2%})', 
                    linewidth=2, color='green')
            
            # Bottom panel - DD for execution
            execution_peak = execution_equity.cummax()
            execution_dd = (execution_equity - execution_peak) / execution_peak * 100
            ax2.plot(self.df_results['date'], execution_dd, label=f'Execution (Max DD: {execution_max_dd:.2%})', 
                    linewidth=2, color='green')
        
        if net:
            net_equity = self.initial_capital + self.df_results["net_pnl"].cumsum()
            ax1.plot(self.df_results['date'], net_equity, label=f'Net (CAGR: {net_cagr:.2%})', 
                    linewidth=2, color='orange')
            
            # Bottom panel - DD for net
            net_peak = net_equity.cummax()
            net_dd = (net_equity - net_peak) / net_peak * 100
            ax2.plot(self.df_results['date'], net_dd, label=f'Net (Max DD: {net_max_dd:.2%})', 
                    linewidth=2, color='orange')
        
        # Format top panel (Equity) - ADD X-AXIS
        ax1.set_title('Equity Curve', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=12)  # ADDED
        ax1.set_ylabel('Portfolio Value', fontsize=12)
        ax1.tick_params(axis='x', labelbottom=True)  # ADDED - Show x-axis labels
        ax1.legend(fontsize=11, loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Format bottom panel (Drawdown)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_title('Drawdown Curve', fontsize=16, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Drawdown (%)', fontsize=12)
        ax2.legend(fontsize=11, loc='best')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved combined chart: {filename}")
        return filename

    #----------------------------------------------------------------------REPORT-----------------------------------------------------------------------------------------------------------------------------#
    """
    Signature:
        Inputs:
            self
            return_type (String): Should be one of "gross", "execution", "net" - will be used to generate the pnl accoordingly
            filename (String) : Name of the pdf file which needs to be generated
            strategy (String): NAmme of the strategy for which we are building the report
            logic (String) : Optional argument , will default to "Confidential", else will print what the user passed in
        Outputs:
            A pdf named <filename>.pdf which will have the following details
                equity_dd_combined.png curve for return_type selected
                distributed_returns table - as generaeted from the distributed_returns_df function for the return type seleced
                ALl other risk/return metrics properly categorised and organised (mentioned in this sheet)
    Purpose: To generate a new pdf file named <filename>.pdf in the same folder as teh code is running and generate a full bt report
        If a file already exits with the name, it will be overwritten
    """
    def generate_report(self, strategy, return_type="execution", logic="Confidential", filename="report.pdf"):

        # Validate return_type
        if return_type not in ["gross", "execution", "net"]:
            logger.error(f"Invalid return_type: {return_type}")
            raise ValueError("return_type must be 'gross', 'execution', or 'net'")
        
        # Create PDF
        if not filename.endswith('.pdf'):
            filename = filename + '.pdf'
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                rightMargin=0.4*inch, leftMargin=0.4*inch,
                                topMargin=0.3*inch, bottomMargin=0.3*inch)  # Reduced margins
        
        # Container for elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom compact styles
        title_style = ParagraphStyle(
            'CompactTitle',
            parent=styles['Heading1'],
            fontSize=16,  # Reduced from 18
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=4,  # Reduced from 6
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CompactHeading',
            parent=styles['Heading2'],
            fontSize=10,  # Reduced from 11
            textColor=colors.HexColor('#34495E'),
            spaceAfter=3,  # Reduced from 4
            spaceBefore=4  # Reduced from 6
        )
        
        # ========== HEADER ==========
        elements.append(Paragraph(f"<b>Backtest Report: {strategy}</b>", title_style))
        
        # METADATA - COMPACT VERTICAL LIST
        metadata = [
            ["Return Type:", return_type.capitalize()],
            ["Initial Capital:", f"${self.initial_capital:,.0f}"],
            ["Strategy Logic:", logic],
            ["Total Trades:", str(self.total_trades())],
            ["Period:", f"{self.df_results['date'].min()} to {self.df_results['date'].max()}"],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")]
        ]
        
        metadata_table = Table(metadata, colWidths=[1.1*inch, 5.1*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),  # Reduced from 9
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # Reduced from 2
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Reduced from 2
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.1*inch))  # Reduced from 0.15
        
        # ========== MAIN CONTENT: CHART + METRICS SIDE BY SIDE ==========
        
        # Generate compact chart
        chart_filename = f"temp_{return_type}_equity_dd.png"
        if return_type == "gross":
            self.combine_equity_dd_curve(gross=True, filename=chart_filename)
        elif return_type == "execution":
            self.combine_equity_dd_curve(execution=True, filename=chart_filename)
        else:
            self.combine_equity_dd_curve(net=True, filename=chart_filename)
        
        # Get all metrics
        total_return = self.total_return_pct()
        cagr = self.cagr_return_pct()
        max_dd = self.max_drawdown_pct()
        calmar = self.calmar_ratio()
        sharpe = self.sharpe_ratio()
        sortino = self.sortino_ratio()
        dd_days = self.max_drawdown_duration_days()
        winrate = self.winrate_pct()
        largest_win = self.largest_win_pct()
        largest_loss = self.largest_loss_pct()
        avg_win = self.avg_win_pct()
        avg_loss = self.avg_loss_pct()
        expectancy = self.expectancy_pct()
        
        # Select index based on return_type
        idx = {"gross": 0, "execution": 1, "net": 2}[return_type]
        
        # Create compact metrics tables
        returns_data = [
            ["RETURNS", ""],
            ["Total Return", f"{total_return[idx]:.2%}"],
            ["CAGR", f"{cagr[idx]:.2%}"],
            ["Total Trades", str(self.total_trades())]
        ]
        
        risk_data = [
            ["RISK", ""],
            ["Max DD", f"{max_dd[idx]:.2%}"],
            ["DD Duration", f"{dd_days[idx]}d"],
            ["Calmar", f"{calmar[idx]:.2f}"],
            ["Sharpe", f"{sharpe[idx]:.2f}"],
            ["Sortino", f"{sortino[idx]:.2f}"]
        ]
        
        winloss_data = [
            ["WIN/LOSS", ""],
            ["Win Rate", f"{winrate[idx]:.2%}"],
            ["Avg Win", f"{avg_win[idx]:.2%}"],
            ["Avg Loss", f"{avg_loss[idx]:.2%}"],
            ["Largest Win", f"{largest_win[idx]:.2%}"],
            ["Largest Loss", f"{largest_loss[idx]:.2%}"],
            ["Expectancy", f"{expectancy[idx]:.2%}"]
        ]
        
        # Create 3 metric tables
        col_w = 0.95*inch  # Slightly reduced
        returns_table = Table(returns_data, colWidths=[col_w, col_w])
        risk_table = Table(risk_data, colWidths=[col_w, col_w])
        winloss_table = Table(winloss_data, colWidths=[col_w, col_w])
        
        # Common style for all metric tables
        metric_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),  # Reduced from 8
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Reduced from 3
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Reduced from 3
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ])
        
        returns_table.setStyle(metric_style)
        risk_table.setStyle(metric_style)
        winloss_table.setStyle(metric_style)
        
        # Arrange chart and metrics side by side - REDUCED CHART HEIGHT
        img = Image(chart_filename, width=4.2*inch, height=2.5*inch)  # Reduced from 3.0
        
        # Put metrics in a single container table (3 tables stacked vertically)
        metrics_container = Table([[returns_table], [risk_table], [winloss_table]])
        metrics_container.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Main layout: chart on left, metrics on right
        main_layout = Table([[img, metrics_container]], colWidths=[4.3*inch, 2.1*inch])
        main_layout.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Reduced from 5
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Reduced from 5
        ]))
        elements.append(main_layout)
        elements.append(Spacer(1, 0.08*inch))  # Reduced from 0.1
        
        # ========== MONTHLY RETURNS TABLE ==========
        elements.append(Paragraph("<b>Monthly Returns (%)</b>", heading_style))
        
        # Get distributed returns
        df_monthly = self.df_results[['date', f'{return_type}_pnl']].copy()
        df_monthly['date'] = pd.to_datetime(df_monthly['date'])
        df_monthly['year'] = df_monthly['date'].dt.year
        df_monthly['month'] = df_monthly['date'].dt.month
        df_monthly['return_pct'] = df_monthly[f'{return_type}_pnl'] / self.initial_capital * 100
        monthly_returns = df_monthly.groupby(['year', 'month'])['return_pct'].sum()
        pivot_table = monthly_returns.reset_index().pivot(index='month', columns='year', values='return_pct')
        pivot_table['Total'] = pivot_table.sum(axis=1)
        yearly_totals = pivot_table.sum(axis=0)
        pivot_table.loc['Total'] = yearly_totals
        
        # Month names
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec', 'Total': 'Total'}
        
        # Convert to list of lists
        monthly_data = [[""] + [str(col) for col in pivot_table.columns]]
        for idx_name in pivot_table.index:
            row = [month_names.get(idx_name, str(idx_name))] + \
                [f"{val:.1f}" if pd.notna(val) else "-" for val in pivot_table.loc[idx_name]]
            monthly_data.append(row)
        
        # Calculate column widths dynamically
        num_cols = len(monthly_data[0])
        col_width = 6.6*inch / num_cols
        
        monthly_table = Table(monthly_data, colWidths=[col_width] * num_cols)
        
        # Style with conditional colors - REDUCED FONT SIZE
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),  # Reduced from 7
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Reduced from 3
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Reduced from 3
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]
        
        # Add conditional coloring
        for row_idx in range(1, len(monthly_data)):
            for col_idx in range(1, len(monthly_data[0])):
                cell_value = monthly_data[row_idx][col_idx]
                if cell_value != "-":
                    try:
                        val = float(cell_value)
                        if val < -1.5:
                            color = colors.HexColor('#ff9999')
                        elif val < -0.5:
                            color = colors.HexColor('#ffcc99')
                        elif val < 0.5:
                            color = colors.HexColor('#ffff99')
                        elif val < 2.0:
                            color = colors.HexColor('#ccff99')
                        elif val < 4.0:
                            color = colors.HexColor('#99ff99')
                        else:
                            color = colors.HexColor('#66ff66')
                        table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), color))
                    except:
                        pass
        
        monthly_table.setStyle(TableStyle(table_style))
        elements.append(monthly_table)
        
        # Build PDF
        doc.build(elements)
        
        # Clean up temporary chart file
        if os.path.exists(chart_filename):
            os.remove(chart_filename)
        
        logger.info(f"Report generated: {filename}")
        return filename