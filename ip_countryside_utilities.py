from config import *;
from ip_countryside_parser import *
#from ip_countryside_parser import get_city
import ipaddress
import sqlite3
import math

from config import *;


def get_record_by_ip(ip):
    ip = bin(int(ipaddress.ip_address(ip)))[2:].zfill(128)
    connection = sqlite3.connect(IP2COUNTRY_DB_SQLLITE)
    cursor = connection.cursor()
    query = "SELECT * FROM ip2country WHERE ip_from <= '%s' and ip_to >= '%s'" % (ip,ip)
    cursor.execute(query)
    result = cursor.fetchall()
    
    if result:
    
        result = result[0]

        ip_from = int(result[0]) 
        ip_to = int(result[1])
        cc = result[2]
        status = result[6]

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
