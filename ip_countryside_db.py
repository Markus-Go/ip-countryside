import json
from config import *;

# record index:    0       1   2    3           4            5          6       7
# record format: ip_from|ip_to|cc|registry|last-modified|record_type|status|description


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
    
    if line.startswith("\n"):
        return []

    line = line.split("|")

    if(len(line) >= 3):

        ip_from         = int(line[0]) 
        ip_to           = int(line[1]) 
        country         = line[2].upper()
        registry        = line[3].upper()
        last_modified   = line[4]
        record_type     = line[5]
        status          = line[6].rstrip("\n")
        descr           = ""
        
        if record_type == "I":
            descr = line[7].rstrip("\n")

        return [ip_from, ip_to, country, registry, last_modified, record_type, status, descr]

    return []


def sort_db(file=IP2COUNTRY_DB):

    records = []

    # get records from final db
    records = read_db(file)

    # sort this list
    records.sort()

    # write sorted list back into final db
    write_db(records, file)


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
                    'Status':        record[6],
                    'Description':   record[7],
                }

                f.write(json.dumps(data, indent=4))
            
                f.write(",\n")
            
            f.write("]")

    except IOError as e:

        print(e)

    return 0


def extract_as_yaml(file=IP2COUNTRY_DB):
    pass
