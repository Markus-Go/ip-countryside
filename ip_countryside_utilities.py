from config import *;
import ipaddress
import math

import pandas as pd


def get_record_by_ip(ip):
    
    col_names = ["ip_from", "ip_to", "cc", "registry", "last-modified", "record_type", "description"]

    df = pd.read_csv(IP2COUNTRY_DB, delimiter="|", names=col_names, converters={'ip_from':int, 'ip_to':int})

    # convert incoming ip from dot notation to int 
    ip = ipaddress.ip_address(ip)
    ip_int = int(ip)
    
    # this is actually not 100% correct. If the Database is clean,
    # there should only be one record returned !
    record = df.loc[ ( (df['ip_from'] <= ip_int) & (df['ip_to'] >= ip_int) ) ].values
    
    if record:
        record = record[0]
    
        cc = record[2]
        if cc:
            return COUNTRY_DICTIONARY[cc], cc
    

def empty_entry_by_idx(records, indicies):
    """
    Set for each index in indicies the corresponding entry in 
    the given list to empty  []

    Arguments
    ----------
    records: list
        List from which entries must be removed

    indicies: list
        List of indicies. 

    Returns
    ----------
    void

    """

    for idx in indicies:

        if idx < len(records):

            records[idx] = []

    records = [x for x in records if x != []]

    return records


def getNetwork(ip_from, ip_to):
    hosts = ip_to + 1 - ip_from 
    res = math.log2(hosts)
    subnetmask = 32 - int(res)
  
    if not res.is_integer():
        print("No valid subnetmask", ip_from, " ", ip_to, "with subnetmask: ", res)
        return
    
        
    return str(ipaddress.ip_address(ip_from)) + "/" + str(subnetmask)





#print(get_record_by_ip("2003:EF:DF13:DCE9:F897:5C93:DA97:4722"))