import json

from config import *;


# @TODO
# Implement an exctract to YAML method      -> Aufwand 5


def read_db(file=IP2COUNTRY_DB):

    records = []
    try:
        # save all records into a list
        with open(file, "r", encoding='utf-8', errors='ignore') as f:
            
            for line in f :
                
                if not line in ['\n', '\r\n']:

                    record = read_db_record(line)
                    
                    if record:
                        
                        records.append(record)
                
    except IOError as e:
        
        print(e)

    return records


def write_db(records, file=IP2COUNTRY_DB):
    
    if not records:
        return

    try:

        with open(file, "w", encoding='utf-8', errors='ignore') as f:
            
            for record in records:
                
                if record:
                    
                    line = "|".join(map(str, record))
                    line = line + '\n'
                    f.write(line)
                    
    except IOError as e:
        
        print(e)

    return records


def read_db_record(line):
    
    # record index:    0       1   2    3           4            5          6
    # record format: ip_from|ip_to|cc|registry|last-modified|record_type|description

    if line.startswith("\n"):
        return []

    line = line.split("|")

    if(len(line) >= 3):

        ip_from         = int(line[0]) 
        ip_to           = int(line[1]) 
        country         = line[2].upper()
        registry        = line[3].rstrip('\n').upper()
        last_modified   = line[4]
        record_type     = line[5].rstrip("\n")
        descr           = ""
        
        if len(line) > 6:
            descr = line[6].rstrip("\n")

        return [ip_from, ip_to, country, registry, last_modified, record_type, descr]

    return []


def extract_as_json(file=IP2COUNTRY_DB):
    
    data = { }
    
    records = read_db(file)
    
    try :

        with open(IP2COUNTRY_DB_JSON, 'w',  encoding='utf-8', errors='ignore') as f:
            
            f.write("[\n")
          
            for record in records:
                
                data = {
                    'IpFrom':        record[0],
                    'IpTo':          record[1],
                    'CountryCode':   record[2],
                    'Registry':      record[3],
                    'LastModified':  record[4],
                    'RecordType':    record[5],
                    'Description':   record[6],
                }

                f.write(json.dumps(data, indent=4))
            
                f.write(",\n")
            
            f.write("]")

    except IOError as e:

        print(e)

    return 0


def extract_as_yaml(file=IP2COUNTRY_DB):
    pass


# later -> sql lite... 