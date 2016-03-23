import numpy as np
import pandas as pd
import json
import datetime, time
import boto3
import cPickle as pickle
from sklearn import preprocessing
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
    Normalize array values.

    INPUT: array
    OUTPUT: array
    '''
    arr = (arr - arr.min()) / (arr.max() - arr.min())
    return arr

def clean_data(df_data):
    '''
    Clean weather data and create features.

    INPUT: dataframe
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
        #  'pressure', 'windspeed',
         'temperaturemax', 'temperaturemin']
    d = ['7']

    for col in c:
        for day in d:
            df[col+day] = pd.rolling_mean(df[col], int(day))

    # create lag features
    c = ['apparenttemperaturemax','apparenttemperaturemin',
         'windspeed']
    d = ['-3', '-7']

    for col in c:
        for day in d:
            df[col+day] = df[col].shift(int(day))

    # impute null values
    df.fillna(0, inplace=True)

    # drop unneeded columns
    df.drop([
            # 'apparenttemperaturemax',
            # 'apparenttemperaturemin',
            'precipintensity',
            'precipintensitymax'],
            axis = 1, inplace=True)

    return df

def predict(df_data):
    '''
    Generate predictions based on model.

    INPUT: dataframe
    OUTPUT: dataframe with predictions
    '''
    df = df_data.copy()
    X = df.values

    # load model
    with open('../model/grid_search_model.pkl') as f:
        model = pickle.load(f)

    df['predict'] = model.predict(X)
    df['slack'] = 1 - df['predict']

    return df
