from config import *;
from ip_countryside_parser import *
#from ip_countryside_parser import get_city
from ipaddress import *
import sqlite3
import math

from config import *;

def get_record_by_ip(ip):
    
    ip = ip_address(ip)
    
    ip = bin(int(ip))[2:].zfill(128)


    connection = sqlite3.connect(IP2COUNTRY_DB_SQLLITE)
    cursor = connection.cursor()
    query = "SELECT * FROM ip2country WHERE ip_from <= '%s' and ip_to >= '%s'" % (ip, ip)
    cursor.execute(query)
    result = cursor.fetchall()
    
    if result:
    
        result = result[0]
        ip_from = ip_address(int(result[0], 2)) 
        ip_to   = ip_address(int(result[1], 2))
        cc      = result[2]
        status  = result[3]

        return [ip_from, ip_to, cc, status]

    else:

        return []


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
    
    return str(ip_address(ip_from)) + "/" + str(subnetmask)

           
def converttoNetwork(records):
                         
    with open(IP2COUNTRY_MM, 'w', encoding='utf-8', errors='ignore') as f:

        for record in records: 
            
            ip_from = int(record[0])
            ip_to = int(record[1])

            ip_from = ip_address(ip_from)
            ip_to = ip_address(ip_to)

            ranges = [ipaddr for ipaddr in summarize_address_range(ip_from, ip_to)]
            
            for range in ranges:
                
                line = "|".join(map(str, [range, record[2]]))
                line = line + '\n'
                f.write(line)           


def traceIP(ip_addr):
    # returns a list of all entries in unmodified databse that contain a certain ip

    ip = int(ip_address(ip_addr))
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
        r[0] =  str(ip_address(int(r[0])))
        r[1] = str(ip_address(int(r[1])))
        r[-1] = r[-1].replace('\n', '')


    return return_list
