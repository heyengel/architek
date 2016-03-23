import numpy as np
import pandas as pd
import json
import forecastio
import datetime, time
import glob
import data_processing
from sql_helper import db_update
from sklearn.ensemble import RandomForestRegressor

# load API key
with open('/Users/Engel/api/keys/forecastio-api.json') as f:
    data = json.load(f)
    api_key = data['api_key']

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

df_daily = df_daily[['apparenttemperaturemax',
 'apparenttemperaturemin', 'precipintensity',
 'precipintensitymax',  'pressure', 'temperaturemax',
 'temperaturemin', 'time', 'windspeed']]

# update SQL database
colnames = ['apparenttemperaturemax', 'apparenttemperaturemin',
           'precipintensity', 'precipintensitymax', 'pressure',
           'temperaturemax', 'temperaturemin', 'time', 'windspeed']

sql_helper.db_update(df_daily, colnames)

#load forecast from database
df_predict_import = pd.read_sql('''SELECT *
                                   FROM forecast_daily
                                   ORDER BY time DESC LIMIT 45''', con=engine)

df_predict = data_processing.clean_data(df_predict_import)

df = data_processing.predict(df_predict)
