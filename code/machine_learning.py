import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime, time
import boto3
import data_processing, api_utils, sql_helper
import cPickle as pickle
from time import time
from operator import itemgetter
from sklearn.ensemble import RandomForestRegressor
from sklearn.grid_search import GridSearchCV

#insert AWS key path here
aws_key_path = '../../api/keys/heyengel-aws.json'

def report(grid_scores, n_top=3):
    '''
    Utility function to report best scores from grid search.
    '''
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
    df_bart = data_processing.clean_data_bart(df_bart_hourly)

    # load forecast.io data from SQL database
    print ('Loading weather data.')
    df_forecast = sql_helper.db_load_weather()

    df = data_processing.clean_data(df_forecast,
                                features=['dayofweek', 'holiday', 'dayofyear',
                                        'pressure', 'apparenttemperaturemin-3'])

    # assign X and y values for model
    df_train = df.copy()
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

    # save to Amazon S3 bucket
    access_key, secret_access_key = api_utils.load_aws_key(aws_key_path)

    session = boto3.session.Session(aws_access_key_id=access_key,
                                    aws_secret_access_key=secret_access_key,
                                    region_name='us-east-1')
    s3 = session.resource('s3')
    bucket_name = 'aws-s3-data'
    s3.meta.client.upload_file('../model/grid_search_model.pkl',
                                bucket_name, Key='grid_search_model.pkl')
    print ('Saved model to S3.')
