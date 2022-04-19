from config import *;
import ipaddress
import math

# @TODO Method should call read_db() to get records in form of list     -> Aufwand 1
# Use a filter instead  

def get_record_by_ip(ip):
    
    with open(IP2COUNTRY_DB, encoding='utf-8', errors='ignore') as file:

        for line in file:

            item = line.split("|")

            range_start = int(item[0])
            range_end   = int(item[1])
            country     = item[2].rstrip('\n')

            if ip_in_range(ip, range_start, range_end):

                return COUNTRY_DICTIONARY[country], country
            

    return False
    

def ip_in_range(ip, start, end):
    
    ip = ipaddress.ip_address(ip)
    ip_int = int(ip)

    return start <= ip_int <= end 


def empty_entry_by_idx(records, indices):
    """
    Set for each index in indices the corresponding entry in 
    the given list to empty  []

    Arguments
    ----------
    records: list
        List from which entries must be removed

    indices: list
        List of indicies. 

    Returns
    ----------
    void

    """

    for idx in indices:

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