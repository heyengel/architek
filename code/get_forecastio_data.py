import numpy as np
import pandas as pd
import forecastio
import datetime, time
from datetime import timedelta, date
import glob, json

#Script for requesting weather data using Forecast.io api

#insert forecast.io API key path here
forecastio_key_path = '../../api/keys/forecastio-api.json'

# load API key
with open(forecastio_key_path) as f:
    data = json.load(f)
    api_key = data['api_key']

# coordinates for Transamerica Pyramid, San Francisco, CA
lat = 37.795184
lng = -122.402764

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

df_list = []

# define start date and end date for data to request
start_date = datetime.datetime(2010, 9, 1, 7, 0, 0)
end_date = datetime.datetime(2011, 1, 1, 7, 0, 0)

# request data from forecast.io using forecastio python wrapper
for single_date in daterange(start_date, end_date):
    forecast = forecastio.load_forecast(api_key, lat, lng, time=single_date)
    timestr = single_date.strftime("%Y%m%d-%H%M%S")

    # save to json files
    with open('../data/forecastio/json/' + timestr + '-forecastio-SF.json', 'w') as outfile:
        json.dump(forecast.json, outfile)

    # extract daily data from json file
    df_tempd = pd.DataFrame(forecast.json['daily']['data'])
    df_list.append(df_tempd)

# combine all dataframes
df_daily = pd.concat(df_list, ignore_index=True, axis=0)

# save dataframe to file
df_daily.to_pickle('../data/forecastio/forecastio_daily.pkl')
