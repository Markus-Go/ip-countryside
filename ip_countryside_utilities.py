import ipaddress
import math
import pandas as pd

from config import *;


def get_record_by_ip(ip):
    
    col_names = ["ip_from", "ip_to", "cc", "registry", "last-modified", "record_type", "status", "description"]

    df = pd.read_csv(IP2COUNTRY_DB, delimiter="|", names=col_names, converters={'ip_from':int, 'ip_to':int})

    # convert incoming ip from dot notation to int 
    ip = ipaddress.ip_address(ip)
    ip_int = int(ip)
    
    # this is actually not 100% correct. If the Database is clean,
    # there should only be one record returned !
    record = df.loc[ ( (df['ip_from'] <= ip_int) & (df['ip_to'] >= ip_int) ) ].values[0]

    record = record.tolist()

    if  record:

        return record

    return False

def converttoNetwork(records):
  
    append_list = []
    for record in records: 
        ip_from = record[0]
        ip_to = record[1]
        hosts = ip_to + 1 - ip_from 
        res = math.log2(hosts)
 
        
        if not res.is_integer() and not record[3] == 'ZZ':
          powers = getPowers(int(hosts)) 
         
        start = ip_from
        end = ip_to
     
        for i in range(len(powers)):
            end = start + powers[i] -1
            append_list.append([start, end, record[3], record[4], record[5]])
            start = end + 1

    # returns a list with split up subnetmasks 
    return append_list


def getPowers(x):

    powers = []
    i = 1
    while i <= x:
        if i & x:
            powers.append(i)
        i <<= 1
    return powers