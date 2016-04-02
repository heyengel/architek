import numpy as np
import pandas as pd
import json
import forecastio
import datetime, time
import data_processing, api_utils
import cPickle as pickle
import sql_helper
import sqlalchemy
from sklearn.ensemble import RandomForestRegressor

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

if __name__ == '__main__':

    #insert forecast.io API key path here
    forecastio_key_path = '../../api/keys/forecastio-api.json'

    # load API key
    api_key = api_utils.load_api_key(forecastio_key_path)

    # coordinates for Transamerica Pyramid
    lat = 37.795184
    lng = -122.402764

    # pull weather forecast from API
    print ('Getting weather forecast.')
    forecast = forecastio.load_forecast(api_key, lat, lng)
    timestr = time.strftime("%Y%m%d-%H%M%S")

    with open('../data/forecastio/api-pull/' + timestr + '-forecastio.json', 'w') as outfile:
        json.dump(forecast.json, outfile)

    df_daily = pd.DataFrame(forecast.json['daily']['data'])
    df_daily.columns = [x.lower() for x in df_daily.columns]

    # specify columns/features to keep
    colnames = ['apparenttemperaturemax', 'apparenttemperaturemin',
               'precipintensity', 'precipintensitymax', 'pressure',
               'temperaturemax', 'temperaturemin', 'time', 'windspeed']

    #update dataframe with specified features
    df_daily = df_daily[colnames]

    # update SQL database
    sql_helper.db_update(df_daily, colnames)

    #load forecast from database
    engine = sqlalchemy.create_engine("postgres://postgres@/forecast")
    conn = engine.connect()
    df_predict_import = pd.read_sql('''SELECT *
                                       FROM forecast_daily
                                       ORDER BY time DESC LIMIT 45''', con=engine)
    conn.close()
    engine.dispose()

    df_predict = data_processing.clean_data(df_predict_import,
                                features=['dayofweek', 'holiday', 'dayofyear',
                                        'pressure', 'apparenttemperaturemin-3'])

    df = predict(df_predict)
    print 'Predictions:'
    print df
