import numpy as np
import pandas as pd
import datetime, time
import boto3
from scipy.stats import scoreatpercentile
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar

def standardize(arr):
    '''
    Standardize array values.

    INPUT: array
    OUTPUT: array
    '''
    arr = (arr - arr.mean()) / float(arr.std(ddof=0))
    return arr

def normalize(arr):
    '''
    Normalize array values between 0 and 1.

    INPUT: array
    OUTPUT: array
    '''
    arr = (arr - arr.min()) / (arr.max() - arr.min())
    return arr


def clean_data(df_data, features=None):
    '''
    Clean weather data and create features.

    INPUT: dataframe, list
    OUTPUT: dataframe
    '''
    df = df_data.copy()
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df = df.resample('1D', how='mean')

    # feature creation
    df['dayofweek'] = pd.DatetimeIndex(df.index).weekday
    df['dayofyear'] = pd.DatetimeIndex(df.index).dayofyear
    df['weekofyear'] = pd.DatetimeIndex(df.index).weekofyear

    # mark holidays
    cal = calendar()
    holidays = cal.holidays(start=df.index.min(), end=df.index.max())
    holidays
    df['holiday'] = 0
    df.loc[df.index.isin(holidays), 'holiday'] = 1

    # rolling means
    c = ['apparenttemperaturemax','apparenttemperaturemin',
         'temperaturemax', 'temperaturemin']
    d = ['7']

    for col in c:
        for day in d:
            df[col+day] = pd.rolling_mean(df[col], int(day))

    # create lag features
    c = ['apparenttemperaturemax','apparenttemperaturemin', 'windspeed']
    d = ['-3', '-7']

    for col in c:
        for day in d:
            df[col+day] = df[col].shift(int(day))

    # impute null values
    df.fillna(0, inplace=True)

    if features is None:
        # drop unneeded columns
        df.drop(['precipintensity', 'precipintensitymax'],
                axis = 1, inplace=True)
    else:
        # use only specified features
        df = df[features]

    return df

def clean_data_bart(df_data):
    '''
    Clean BART data, trim outliers and normalize rider counts.

    INPUT: dataframe
    OUTPUT: dataframe
    '''
    df_bart_hourly = df_data.copy()
    # filter exits counts from 5am-11am
    df_bart = df_bart_hourly.ix[datetime.time(5):datetime.time(11)]

    # combine to daily counts
    df_bart = df_bart.resample('1D', how={'counts': np.sum})

    # trim upper outliers 99 percentile
    upper_limit = df_bart.counts > scoreatpercentile(df_bart.counts, 99)
    df_bart[df_bart.counts > scoreatpercentile(df_bart.counts, 99)] = scoreatpercentile(df_bart.counts, 99)

    # low outliers
    lower_limit = (df_bart.counts.isnull()) | (df_bart.counts < 4000)
    impute_dict = {'2012-10-31': 100000, '2011-10-15': 25000, '2011-10-16': 12000, '2011-11-05': 25000,
    '2011-12-25': 4000, '2012-11-03': 12000, '2012-12-25': 4000,
    '2013-07-01': 95000, '2013-07-02': 95000, '2013-07-03': 90000,
    '2013-07-04': 13000, '2013-07-05': 18000, '2013-10-18': 85000,
    '2013-10-19': 25000, '2013-10-20': 12000, '2013-10-21': 92000}
    for key, val in impute_dict.iteritems():
        df_bart.ix[key]['counts'] = val

    # normalize bart counts and detrend
    xx = np.arange(1826) # 1826 days
    yy = 80000 + xx * 18.5 # equation based on growth trend
    df_bart['counts_normed'] = (df_bart.counts - df_bart.counts.min()) / (yy - df_bart.counts.min())

    return df_bart
