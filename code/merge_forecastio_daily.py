import numpy as np
import pandas as pd
import glob, boto3, json
import merge_data
import sql_helper
import sqlalchemy


# collect filenames
path =r'../data/forecastio/daily/'
filenames = glob.glob(path + "/*-SF.pkl")
for i, filename in enumerate (filenames):
    print i+1, filename

# save dataframes to file
df_forecastio = merge_data.merge_data(filenames)
df_forecastio.columns = [x.lower() for x in df_forecastio.columns]
df_forecastio = df_forecastio[['apparenttemperaturemax',
 'apparenttemperaturemin', 'precipintensity', 'precipintensitymax',
 'pressure', 'temperaturemax', 'temperaturemin', 'time', 'windspeed']]

# drop duplicate entry
df_forecastio.drop(1919, inplace=True)
df_forecastio.to_pickle(path + 'df_forecastio_daily.pkl')

# connect to Postgres SQL database
engine = sqlalchemy.create_engine("postgres://postgres@/forecast")
conn = engine.connect()

# save to Postgres SQL database
df_forecastio.to_sql('forecast_daily', engine, if_exists='replace', index=False)
conn.close()
engine.dispose()

# set primary database key
sql_helper.db_setkey('forecast', 'time')

# save to Amazon S3 bucket
with open('/users/engel/api/keys/heyengel-aws.json') as f:
    data = json.load(f)
    access_key = data['access-key']
    secret_access_key = data['secret-access-key']

session = boto3.session.Session(aws_access_key_id=access_key,
                                aws_secret_access_key=secret_access_key,
                                region_name='us-east-1')
s3 = session.resource('s3')
bucket_name = 'aws-s3-data'
s3.meta.client.upload_file('../data/forecastio/daily/df_forecastio_daily.pkl',
                    bucket_name, Key='forecastio/daily/df_forecastio_daily.pkl')
