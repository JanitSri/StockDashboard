import numpy as np
import pandas as pd
import datetime
import time
import concurrent.futures

def clean_data(ticker_eod):
    """
    Get the ticker end of day data and clean the data
    
    Parameters:
        ticker_eod: The end of day data for the ticker 
         
    Returns:
        cleaned_data: The cleaned data returned in a pandas dataframe
    """
    
    eod_data = [x for x in ticker_eod]
    
    # ticker dataframer
    #"Date", "Open", "High", "Low", "Close", "Volume", "AdjClose"
    cleaned_data = pd.DataFrame(eod_data, columns = ["Date", "Open", "High", "Low", "Close", "Volume", "AdjClose"])
    cleaned_data['Date'] = cleaned_data['Date'].apply(lambda d: d.strftime(r'%Y-%m-%d'))
    cleaned_data.set_index('Date', inplace=True)
    cleaned_data = cleaned_data.apply(pd.to_numeric, errors="ignore")
    
    # last day calculation 
    last_day_in_df = cleaned_data.tail(1).index.item()
    
    if(last_day_in_df >= datetime.date.today().strftime("%Y-%m-%d")):
        cleaned_data.drop(cleaned_data.tail(1).index,inplace=True) 
    
    return cleaned_data
    

def atr_calculation(eod_df):
    """
    Calculate the average true range (atr) for the ticker 
    
    Parameters:
        eod_df: The pandas dataframe with the eod data 
         
    Returns:
        atr_data: The pandas column with the atr calculated data
    """
    
    # copy the dataframe 
    ticker_df = eod_df.copy()
    
    # ATR CALCULATIONS 
    # ^formula --> Current ATR = [(Prior ATR x 13) + Current TR] / 14
    ticker_df['CH_PC'] = np.abs(np.subtract(ticker_df['High'], ticker_df['Close'].shift(1)))  # current high - previous close 
    ticker_df['CL_PC'] = np.abs(np.subtract(ticker_df['Low'], ticker_df['Close'].shift(1)))  # current low - previous close 
    ticker_df['CH_CL'] = np.abs(np.subtract(ticker_df['High'], ticker_df['Low']))  # current high - current low
    ticker_df['TR'] = ticker_df[['CH_PC', 'CL_PC', 'CH_CL']].max(axis=1)
    ticker_df['TR'] = ticker_df['TR'].round(4)
    
    ticker_df['TEMP_ATR'] = ticker_df['TR'].rolling(14).mean()           
    
    atr = ticker_df['TEMP_ATR'].values
    tr = ticker_df['TR'].values
    atr_data = [0] * len(atr)
    
    for x in range(len(atr)):
        if x < 14:
            atr_data[x] = atr[x]
        else:
            atr_data[x] = ((atr[x-1] * 13) + tr[x]) / 14
            atr[x] = atr_data[x]
    
    return atr_data
    

def exponential_moving_average_calculation(eod_df):
    """
    Calculate the exponential moving average (ema) for the ticker 
    
    Parameters:
        eod_df: The pandas dataframe with the eod data 
         
    Returns:
        ema_data: The pandas column with the ema calculated data
    """
    
    # copy the dataframe 
    ticker_df = eod_df.copy()
    
    # EXPONENTIAL MOVING AVERAGE 
    ticker_df['EMA_5'] = ticker_df['Close'].ewm(span=5,adjust=False).mean()  # daily
    ticker_df['EMA_21'] = ticker_df['Close'].ewm(span=21,adjust=False).mean()  # one month
    ticker_df['EMA_63'] = ticker_df['Close'].ewm(span=63,adjust=False).mean()  # three month 
    ticker_df['EMA_126'] = ticker_df['Close'].ewm(span=126,adjust=False).mean()  # six month 
    ticker_df['EMA_252'] = ticker_df['Close'].ewm(span=252,adjust=False).mean()  # year 
    
    ema_data = ticker_df[['EMA_5','EMA_21','EMA_63','EMA_126','EMA_252']]
    
    return ema_data
    

def rsi_calculation(eod_df):
    """
    Calculate the relative strength index (rsi) for the ticker 
    
    Parameters:
        eod_df: The pandas dataframe with the eod data 
         
    Returns:
        rsi_data: The pandas column with the rsi calculated data
    """
    
    # copy the dataframe 
    ticker_df = eod_df.copy()
    
    # RSI CALCULATIONS 
    ticker_df['Advance'] = np.where((ticker_df['Close'] >= ticker_df['Close'].shift(1)), (ticker_df['Close'] - ticker_df['Close'].shift(1)), 0)
    ticker_df['Decline'] = np.where((ticker_df['Close'] <= ticker_df['Close'].shift(1)), (ticker_df['Close'] - ticker_df['Close'].shift(1)), 0)
    # ^formula --> Current Close - Prev. Close 
    
    ticker_df['Advance'] = ticker_df['Advance'].abs()
    ticker_df['Decline'] = ticker_df['Decline'].abs()
    
    ticker_df['Average_Advance'] = 0
    ticker_df = ticker_df[ticker_df['Average_Advance'].notnull()].copy()
    ticker_df.loc[13:14, 'Average_Advance'] = pd.Series(ticker_df['Advance']).rolling(window=14).mean()
    # ^formula --> First Average Gain = Sum of Gains over the past 14 periods / 14
    
    average_advance = ticker_df['Average_Advance'].values
    advance = ticker_df['Advance'].values
    final_average_advance = [0] * len(average_advance)
    
    for x in range(len(average_advance)):
        if x < 14:
            final_average_advance[x] = average_advance[x]
        else:
            final_average_advance[x] = ((average_advance[x-1] * 13) + advance[x]) / 14
            average_advance[x] = final_average_advance[x]
    
    ticker_df = ticker_df.assign(Final_Average_Advance=final_average_advance)
    
    ticker_df['Average_Decline'] = 0
    ticker_df = ticker_df[ticker_df['Average_Decline'].notnull()].copy()
    ticker_df.loc[13:14, 'Average_Decline'] = pd.Series(ticker_df['Decline']).rolling(window=14).mean()
    
    average_decline = ticker_df['Average_Decline'].values
    decline = ticker_df['Decline'].values
    final_average_decline = [0] * len(average_decline)
    
    for x in range(len(average_decline)):
        if x < 14:
            final_average_decline[x] = average_decline[x]
        else:
            final_average_decline[x] = ((average_decline[x-1] * 13) + decline[x]) / 14
            average_decline[x] = final_average_decline[x]
    
    
    ticker_df = ticker_df.assign(Final_Average_Decline=final_average_decline)
    
    ticker_df['RS'] = ticker_df['Final_Average_Advance'] / ticker_df['Final_Average_Decline']
    ticker_df['RSI'] = 100 - (100 / (1 + ticker_df['RS']))
    
    rsi_data = ticker_df[['RSI']]
    
    return rsi_data
    

def bollinger_bands_calculation(eod_df):
    """
    Calculate the bollinger bands for the ticker 
    
    Parameters:
        eod_df: The pandas dataframe with the eod data 
         
    Returns:
        bb_data: The pandas column with the bollinger bands calculated data
    """
    
    # copy the dataframe 
    ticker_df = eod_df.copy()
    
    # BOLLINGER BANDS
    ticker_df['BB_20MA'] = ticker_df['Close'].rolling(window=20).mean()
    ticker_df['20STD'] = ticker_df['Close'].rolling(window=20).std(ddof=0)  # population
    ticker_df['BB_UpperBands'] = ticker_df['BB_20MA'] + (ticker_df['20STD'] * 2)
    ticker_df['BB_LowerBands'] = ticker_df['BB_20MA'] - (ticker_df['20STD'] * 2)
    
    bb_data = ticker_df[['BB_20MA', 'BB_UpperBands','BB_LowerBands']]
    
    return bb_data
    

def macd_calculation(eod_df):
    """
    Calculate the Moving Average Convergence Divergence (macd) for the ticker 
    
    Parameters:
        eod_df: The pandas dataframe with the eod data 
         
    Returns:
        macd_data: The pandas column with the macd calculated data
    """
    
    # copy the dataframe 
    ticker_df = eod_df.copy()
    
    # MACD 
    ticker_df['MACD_12EMA'] = ticker_df['Close'].ewm(span=12,adjust=False).mean()
    ticker_df['MACD_26EMA'] = ticker_df['Close'].ewm(span=26,adjust=False).mean()
    ticker_df['MACD'] = ticker_df['MACD_12EMA'] - ticker_df['MACD_26EMA'] 
    ticker_df['Signal_Line'] = ticker_df['MACD'].ewm(span=9,adjust=False).mean() 
    ticker_df['MACD_Histogram'] = ticker_df['MACD'] - ticker_df['Signal_Line']
    ticker_df['MACDHist_POSorNEG'] = np.where((ticker_df['MACD_Histogram'] >= 0), 'POSITIVE', 'NEGATIVE')
    ticker_df['MACD_Change'] = np.where((ticker_df['MACDHist_POSorNEG'].eq(ticker_df['MACDHist_POSorNEG'].shift())), False, True)  # to see if the hist changes from positive to negative 
    
    macd_data = ticker_df[['MACD','Signal_Line','MACD_Histogram']]
    
    return macd_data
    
    
def correlation_coefficient_calculation(eod_df, sp500_data):
    """
    Calculate the correlation coefficient for the ticker with the S&P 500
    
    Parameters:
        eod_df: The pandas dataframe with the eod data 
        sp500_data: The S&P 500 data for the correlation calculation    
         
    Returns:
        cc_data: The pandas column with the correlation coefficient calculated data 
    """
        
    # copy the dataframe 
    ticker_df = eod_df.copy()
    
    # get the S&P 500 dataframe 
    df_SP500 = clean_data(sp500_data)
    
   
    # CORRELATION COEFFICIENT        
    ticker_df['TickerClose'] = ticker_df['Close']
    TickerStart = ticker_df.index[0]
           
    main_df = df_SP500.loc[TickerStart:].join(ticker_df['TickerClose'])
         
    x = main_df['Close']
    y = main_df['TickerClose']
               
    main_df['SP500ROLL_CORR'] = x.rolling(window=5).corr(other=y) #5 Day Correlation
    
    cc_data = main_df[['SP500ROLL_CORR']]
    
    return cc_data
       
       
def daily_movements_calculation(eod_df):
    """
    Calculate the daily movements for the ticker using the exponential moving average
    with a window of 10 days
    
    Parameters:
        eod_df: The pandas dataframe with the eod data 
         
    Returns:
        daily_movements_data: The pandas column with the daily movements calculated data
    """
    
    # copy the dataframe 
    ticker_df = eod_df.copy()
    
    # FIND THE DAILY MOVEMENTS (USING EXPONENTIAL MOVING AVERAGE)
    ticker_df['Daily Movement'] = ticker_df['High'] - ticker_df['Low']
    ticker_df['Daily Movement EMA'] = ticker_df['Daily Movement'].ewm(span=10,adjust=False).mean() 
    
    daily_movements_data = ticker_df[['Daily Movement EMA']]
    
    return daily_movements_data


def get_techical_indicators(ticker_data, sp500_data):
    """
    Calculate various techincal indicators for a stock   
    
    Parameters:
        ticker_data: The end of day data for the ticker
        sp500_data: The end of day data for S&P 500
         
    Returns:
        df: The pandas dataframe with the calculated technical indicators
    """
    
    #pd.set_option('display.max_columns', None)
    
    # clean the data
    df = clean_data(ticker_data)
    
    # average true range calculation 
    atr_calculated_data = atr_calculation(df)
    df = df.assign(ATR=atr_calculated_data)
    df['ATR'] = pd.to_numeric(df['ATR'],errors='coerce').fillna(0)
    
    # exponential moving average calculation
    ema_calculated_data = exponential_moving_average_calculation(df)
    df = df.join(ema_calculated_data)
    
    # relative strength index calculation 
    rsi_calculated_data = rsi_calculation(df)
    df = df.join(rsi_calculated_data)
    df['RSI'] = pd.to_numeric(df['RSI'],errors='coerce').fillna(0)
    
    # bollinger bands calculation 
    bb_calculated_data = bollinger_bands_calculation(df)
    df = df.join(bb_calculated_data)
    df['BB_20MA'] = pd.to_numeric(df['BB_20MA'],errors='coerce').fillna(0)
    df['BB_UpperBands'] = pd.to_numeric(df['BB_UpperBands'],errors='coerce').fillna(0)
    df['BB_LowerBands'] = pd.to_numeric(df['BB_LowerBands'],errors='coerce').fillna(0)
    
    # moving average convergence divergence
    macd_data = macd_calculation(df)
    df = df.join(macd_data)
    
    # correlation coefficient calculation 
    cc_data = correlation_coefficient_calculation(df, sp500_data)
    df = df.join(cc_data)
    df['SP500ROLL_CORR'] = pd.to_numeric(df['SP500ROLL_CORR'], errors='coerce').fillna(0).map("{:.2%}".format)
    
    # daily movements calculation
    dm_data = daily_movements_calculation(df)
    df = df.join(dm_data)
    
    # rounding of the data 
    df = df.round(2)

    df.to_csv('test.csv')

    output = df.to_dict('index')

    return output
