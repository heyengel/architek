import numpy as np
import pandas as pd
import glob, boto3, json

def merge_bart(filenames, stations):
    '''
    INPUT: list, list
    OUTPUT: dataframe

    Merge BART data into a pandas dataframe for the specified exit stations.
    '''
    df_list = []
    dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H')

    for filename in filenames:
        df_temp = pd.read_csv(filename,
                compression='gzip',
                header=None,
                dtype={1: str})
                # parse_dates={'datetime': [0, 1]}, date_parser=dateparse)
        df_temp.columns=['date', 'hour', 'origin', 'exit', 'counts']
        # filter based on exit stations
        df_temp = df_temp[df_temp['exit'].isin(stations)]
        df_list.append(df_temp)

    # combines list into a single dataframe
    df_all = pd.concat(df_list, ignore_index=True, axis=0)
    # convert to datetime
    df_all['date'] = pd.to_datetime(df_all['date'] + '-' + df_all['hour'],
                                                    format='%Y-%m-%d-%H')
    df_all.set_index('date', inplace=True)
    return df_all

if __name__ == '__main__':
    # collect filenames
    path =r'../data/bart/'
    filenames = glob.glob(path + "/*.csv.gz")
    for i, filename in enumerate (filenames):
        print i+1, filename

    # BART exit stations
    stations = ['EM', 'MT', 'PL', 'CC']

    # save dataframes to file
    df_bart = merge_bart(filenames, stations)
    df_bart.to_pickle(path + 'df_bart.pkl')

    # save to S3
    with open('/users/engel/api/keys/heyengel-aws.json') as f:
        data = json.load(f)
        access_key = data['access-key']
        secret_access_key = data['secret-access-key']

    session = boto3.session.Session(aws_access_key_id=access_key,
                                    aws_secret_access_key=secret_access_key,
                                    region_name='us-east-1')
    s3 = session.resource('s3')
    bucket_name = 'aws-s3-data'
    s3.meta.client.upload_file('../data/bart/df_bart.pkl',
                                    bucket_name, Key='df_bart.pkl')
