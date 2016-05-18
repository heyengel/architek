import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def db_setkey(database_name, table_name, column_name):
    '''
    set primary database key.
    '''
    con = psycopg2.connect(database=database_name, user='postgres')
    cur = con.cursor()

    cur.execute('ALTER TABLE {} ADD PRIMARY KEY ({});'.format(table_name, column_name))

    con.commit()
    cur.close()

def db_update(df, colnames, passwd=None):
    '''
    insert and update SQL database.

    INPUT: dataframe, list, string
    OUTPUT: none
    '''
    con = psycopg2.connect(database='forecast', user='postgres')
    cur = con.cursor()

    for x in range(0,len(df)):
        cur.execute('INSERT INTO forecast_daily (' + \
                    ', '.join(['%s'] * len(df.columns)) % tuple(df.columns) + \
                    ') VALUES (' + ', '.join(['%s'] * len(df.columns)) % tuple(df.iloc[x].values) + \
                    ') ON CONFLICT ON CONSTRAINT forecast_daily_pkey DO UPDATE SET (' + \
                    ', '.join(['%s'] * len(df.columns)) % tuple(df.columns) + ') = (' + \
                    ', '.join(['%s'] * len(df.columns)) % tuple(df.iloc[x].values) + ');')
    con.commit()
    cur.close()

# check pyscopg2 docs 'SQL injection'

def db_load_weather():
    '''
    Load from SQL database and return dataframe.

    INPUT: string
    OUTPUT: dataframe
    '''
    engine = create_engine("postgres://postgres@/forecast")
    conn = engine.connect()
    df_forecast = pd.read_sql("SELECT * FROM forecast_daily", con=engine)
    conn.close()
    engine.dispose()
    return df_forecast
