import numpy as np
import pandas as pd
import glob, json
import merge_data


def merge_data(filenames):
    '''
    INPUT: list, int
    OUTPUT: dataframe

    Merge list of files into a single pandas dataframe.
    '''
    df_list = []
    for filename in filenames:
        df_temp = pd.read_pickle(filename)
        df_list.append(df_temp)

    # combines list into a single dataframe
    df_all = pd.concat(df_list, ignore_index=True, axis=0)

    return df_all
