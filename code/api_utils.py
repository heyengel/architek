import json

def load_aws_key(keypath):
    '''
    Return AWS keys.

    INPUT: string
    OUTPUT: string, string
    '''
    with open(keypath) as f:
        data = json.load(f)
    return data['access-key'], data['secret-access-key']

def load_api_key(keypath):
    '''
    Return API key.

    INPUT: string
    OUTPUT: string
    '''
    with open(keypath) as f:
        data = json.load(f)
    return data['api_key']
