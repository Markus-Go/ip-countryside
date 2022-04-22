from netaddr import IPSet
from mmdb_writer import MMDBWriter
import maxminddb
import ipaddress
from ipaddress import ip_address, IPv4Address, IPv6Address, ip_interface
import json
import json
import yaml
import math
from config import *;


# @TODO
# Implement an exctract to YAML method      -> Aufwand 5


def read_db(file=IP2COUNTRY_DB):

    records = []
    try:

        # save all records into a list
        with open(file, "r", encoding='utf-8', errors='ignore') as f:
            
            for line in f:
                
                record = read_db_record(line)
                
                if record:
                    
                    records.append(record)

    except IOError as e:
        
        print(e)

    return records


def read_db_record(line):
    
    # record index:    0       1   2    3           4            5          
    # record format: ip_from|ip_to|cc|registry|last-modified|description

    if line.startswith("\n"):
        return []

    line = line.split("|")

    if(len(line) >= 3):

        ip_from         = int(line[0]) 
        ip_to           = int(line[1]) 
        country         = line[2].upper()
        registry        = line[3].rstrip('\n').upper()
        last_modified   = ""
        descr           = ""

        if len(line) >= 5:
            last_modified = line[4].rstrip("\n")

        if len(line) >= 6:
            descr = line[5].rstrip("\n")

        return [ip_from, ip_to, country, registry, last_modified, descr]

    return []


def extract_as_json(file=IP2COUNTRY_DB):
    
    data = { }
    
    records = read_db(file)
    
    try :

        with open(IP2COUNTRY_DB_JSON, 'w',  encoding='utf-8', errors='ignore') as f:
            
            f.write("[\n")
          
            for recod in records:
                
                data = {
                    'IpFrom':        recod[0],
                    'IpTo':          recod[1],
                    'CountryCode':   recod[2],
                    'Registry':      recod[3],
                    'LastModified':  recod[4],
                    'Description':   recod[5],
                }

                f.write(json.dumps(data, indent=4))
            
                f.write(",\n")
            
            f.write("]")

    except IOError as e:

        print(e)

    return 0


def extract_as_yaml(file=IP2COUNTRY_DB):
    
    data = { }
    
    
    records = read_db(file)
    
    try :

        with open(IP2COUNTRY_DB_YAML, 'w',  encoding='utf-8', errors='ignore') as f:
            
            f.write("---\n")
          
            for record in records:
                
             
                f.write("- IpFrom: " )
                f.write(str(record[0]))
                f.write("\n  IpTo: ")
                f.write(str(record[1]))
                f.write("\n  CountryCode: ")
                f.write(record[2])
                f.write("\n  Registry: ")
                f.write(record[3])
                f.write("\n  LastModified: ")
                f.write(record[4])
                f.write("\n  Description: ")
                f.write(record[5])
                f.write("\n")


           

    except IOError as e:

        print(e)
                

    return 0

def extract_as_mmdb(file=IP2COUNTRY_DB):
    data = {}

    records = read_db(file)

    writerv4 = MMDBWriter(ip_version=4)
    writerv6 = MMDBWriter(ip_version=6)
    for record in records:
        ipaddress = getNetwork(record[0], record[1])
        ipversion = ip_interface(ipaddress).ip.version
        if ipversion == 4:
            try:
                writerv4.insert_network(IPSet(['{0}'.format(ipaddress)]),
                                        {'CountryCode': '{0}'.format(record[2]),
                                         'Registry': '{0}'.format(record[3]),
                                         'LastModified': '{0}'.format(record[4]),
                                         'Description': '{0}'.format(record[5])})
                writerv4.to_db_file(IP2COUNTRY_DB_MMDB_V4)
                print("entry added for: " + ipaddress)

            except IOError as e:
                #print(e)
                return 0

        if ipversion == 6:
            try:
                writerv6.insert_network(IPSet(['{0}'.format(ipaddress)]),
                                        {'CountryCode': '{0}'.format(record[2]),
                                         'Registry': '{0}'.format(record[3]),
                                         'LastModified': '{0}'.format(record[4]),
                                         'Description': '{0}'.format(record[5])})
                writerv6.to_db_file(IP2COUNTRY_DB_MMDB_V6)
                print("entry added for: " + ipaddress)

            except IOError as e:
                #print(e)
                return 0

def read_mmdb(ipaddress):
    if ip_interface(ipaddress).ip.version == 4:
        m = maxminddb.open_database(IP2COUNTRY_DB_MMDB_V4)
    else:
        m = maxminddb.open_database(IP2COUNTRY_DB_MMDB_V6)
    return m.get(ipaddress)

def getNetwork(ip_from, ip_to):
    hosts = ip_to + 1 - ip_from
    res = math.log2(hosts)
    subnetmask = 32 - int(res)
    if subnetmask < 0:
        subnetmask = subnetmask * -1
    if not res.is_integer():
        round(subnetmask, 0)
        #print("No valid subnetmask", ip_from, " ", ip_to, "with subnetmask: ", res)
        return str(ipaddress.ip_address(ip_from)) + "/" + str(subnetmask)

    return str(ipaddress.ip_address(ip_from)) + "/" + str(subnetmask)

def getaddress(ip_from):
    return str(ipaddress.ip_address(ip_from))

#extract_as_mmdb()
print(read_mmdb("131.255.44.4"))
print(read_mmdb("2c0f:eca0::0001"))

