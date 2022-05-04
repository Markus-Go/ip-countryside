import ipaddress
import math
import pandas as pd

from config import *;


from config import *;


def get_record_by_ip(ip):
    
    col_names = ["ip_from", "ip_to", "cc", "registry", "last-modified", "record_type", "status", "description"]

    df = pd.read_csv(IP2COUNTRY_DB, delimiter="|", names=col_names, converters={'ip_from':int, 'ip_to':int})

    # convert incoming ip from dot notation to int 
    ip = ipaddress.ip_address(ip)
    ip_int = int(ip)
    
    # this is actually not 100% correct. If the Database is clean,
    # there should only be one record returned !
    record = df.loc[ ( (df['ip_from'] <= ip_int) & (df['ip_to'] >= ip_int) ) ].values

    if len(record) > 0:

        record = record[0].tolist()
        return record

    return False



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


def converttoNetwork(records):
                         
    with open(IP2COUNTRY_MM, 'w', encoding='utf-8', errors='ignore') as f:

        for record in records: 
            powers = []
            ip_from = int(record[0])
            ip_to = int(record[1])
            hosts = ip_to + 1 - ip_from 
            res = math.log2(hosts)
 
        
            if not res.is_integer() and not record[3] == 'ZZ':
                powers = getPowers(int(hosts)) 
         
                start = ip_from
                end = ip_to
          
                for i in range(len(powers)):
                    end = start + powers[i] -1
                    line = "|".join(map(str, [start, end, record[2], record[3], record[4], record[5]]))
                    line = line + '\n'
                    f.write(line)   
                    start = end + 1
            else:
                    line = "|".join(map(str, record))
                    line = line + '\n'
                    f.write(line)
     

def getPowers(x):

    powers = []
    i = 1
    while i <= x:
        if i & x:
            powers.append(i)
        i <<= 1
    return powers


def traceIP(ip_addr):
    # returns a list of all entries in unmodified databse that contain a certain ip

    ip = int(ipaddress.ip_address(ip_addr))
    return_list = []

    with open(TRACE_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        i = 0
        for line in f:
            # in case there is still newlines in the database
            if line != '\n':
                entry = line.split('|')
                ip_from = int(entry[0])
                ip_to = int(entry[1])
                if ip_from <= ip and ip_to >= ip:
                    return_list.append(entry)

            
    for r in return_list:
        r[0] =  str(ipaddress.ip_address(int(r[0])))
        r[1] = str(ipaddress.ip_address(int(r[1])))
        r[-1] = r[-1].replace('\n', '')


    return return_list


#print(get_record_by_ip("2003:EF:DF13:DCE9:F897:5C93:DA97:4722"))