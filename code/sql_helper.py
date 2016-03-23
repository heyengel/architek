import psycopg2

def db_setkey(database, key_col):
    '''
    set primary database key.
    '''
    con = psycopg2.connect(database=database, user='postgres')
    cur = con.cursor()

    cur.execute('ALTER TABLE forecast_daily ADD PRIMARY KEY (%s);' % (key_col))

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
