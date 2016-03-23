import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import datetime, time
import boto3
import data_processing
import cPickle as pickle
from data_processing import clean_data
from time import time
from scipy.stats import scoreatpercentile
from sqlalchemy import create_engine
from operator import itemgetter
from sklearn.ensemble import RandomForestRegressor
from sklearn.grid_search import GridSearchCV

#insert AWS key path here
aws_key_path = '../../api/keys/heyengel-aws.json'

# Utility function to report best scores
def report(grid_scores, n_top=3):
    top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
              score.mean_validation_score,
              np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")

if __name__ == '__main__':

    # load BART data
    print ('Loading BART data.')
    df_bart_import = pd.read_pickle('../data/bart/df_bart_hourly.pkl')
    df_bart_hourly = df_bart_import.copy()

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

    # load forecast.io data from SQL database
    print ('Loading weather data.')
    engine = create_engine("postgres://postgres@/forecast")
    conn = engine.connect()
    df_forecast = pd.read_sql("SELECT * FROM forecast_daily", con=engine)
    conn.close()
    engine.dispose()

    df = clean_data(df_forecast)

    # assign X and y values for model
    df_train = df.copy()
    df_train = df_train[['dayofweek', 'holiday', 'dayofyear',
                        'pressure', 'apparenttemperaturemin-3']]
    y = df_bart['20110101':'20151231'].counts_normed.values
    X = df_train['20110101':'20151231'].values

    # build a classifier
    clf = RandomForestRegressor()

    # use a full grid over all parameters
    param_grid = {'max_depth': [10, 15, 20, 30, None],
                  'max_features': ['sqrt', 'log2', None],
                  'min_samples_split': [1, 2, 4, 6, 8],
                  'min_samples_leaf': [1, 2, 4, 6, 8],
                  'bootstrap': [True, False],
                  'n_estimators': [40, 60, 80, 100, 200]}

    # run grid search
    print ('Starting Grid Search.')
    grid_search = GridSearchCV(clf, param_grid=param_grid, n_jobs=-1)
    start = time()
    grid_search.fit(X, y)

    print("GridSearchCV took %.2f seconds for %d candidate parameter settings."
          % (time() - start, len(grid_search.grid_scores_)))
    report(grid_search.grid_scores_)

    # pickle the model
    model = grid_search.best_estimator_
    with open('../model/grid_search_model.pkl', 'w') as f:
            pickle.dump(model, f)
    print ('Saved model locally.')

    # save model to AWS S3
    with open(aws_key_path) as f:
        data = json.load(f)
        access_key = data['access-key']
        secret_access_key = data['secret-access-key']

    session = boto3.session.Session(aws_access_key_id=access_key,
                                    aws_secret_access_key=secret_access_key,
                                    region_name='us-east-1')
    s3 = session.resource('s3')
    bucket_name = 'aws-s3-data'
    s3.meta.client.upload_file('../model/grid_search_model.pkl',
                                bucket_name, Key='grid_search_model.pkl')
    print ('Saved model to S3.')
