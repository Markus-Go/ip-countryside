from netaddr import IPSet
from mmdb_writer import MMDBWriter
import maxminddb
import ipaddress
from ipaddress import ip_address, IPv4Address, IPv6Address, ip_interface
import json
#import yaml
import math
import sqlite3
import csv
import random
from config import *;

from operator import itemgetter
from sort import large_sort

from config import *

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

    with (open(file, "r", encoding='utf-8', errors='ignore')) as input, open(os.path.join(DEL_FILES_DIR, "ip2country_temp.db"), "w", encoding='utf-8', errors='ignore') as output:

        large_sort(input, output, itemgetter(1,2), False)

    os.remove(IP2COUNTRY_DB)
    os.rename(os.path.join(DEL_FILES_DIR, "ip2country_temp.db"), IP2COUNTRY_DB)


def extract_as_json(file=IP2COUNTRY_DB):
    
    data = { }
    
    records = read_db(file)
    
    try :

        with open(IP2COUNTRY_DB_JSON, 'w',  encoding='utf-8', errors='ignore') as f:
            
            f.write("[\n")
          
            for record in records:
                data = {
                    'ip_from':        record[0],
                    'ip_to':          record[1],
                    'cc':               record[2],
                    'registry':         record[3],
                    'last_modified':  record[4],
                    'record_type':        record[5],
                    'status':        record[6],
                    'description':   record[7],
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
             
                f.write("- ip_from: " )
                f.write(str(record[0]))
                f.write("\n  ip_to: ")
                f.write(str(record[1]))
                f.write("\n  cc: ")
                f.write(record[2])
                f.write("\n  registry: ")
                f.write(record[3])
                f.write("\n  last_modified: ")
                f.write(record[4])
                f.write("\n  record_type: ")
                f.write(record[5])
                f.write("\n  status: ")
                f.write(record[6])
                f.write("\n  description: ")
                f.write(record[7])
                f.write("\n")

    except IOError as e:

        print(e)
       
    return 0

def extract_as_sqllite(file=IP2COUNTRY_DB):
    os.remove(IP2COUNTRY_DB_SQLLITE)

    connection = sqlite3.connect(IP2COUNTRY_DB_SQLLITE)
    cursor = connection.cursor()

    #ip_from|ip_to|country|ria|date|file|description
    
    query = """
    CREATE TABLE ip2country (
    ip_from VARCHAR(129),
    ip_to VARCHAR(129),
    cc varchar(3),
    registry VARCHAR(15), 
    last_modified VARCHAR(15), 
    record_type VARCHAR(2),
    status VARCHAR(30),
    description VARCHAR(255),
    PRIMARY KEY (ip_from, ip_to)
    );    
    """

    cursor.execute(query)
    connection.commit()

    #query = "CREATE INDEX ip_range on ip2country (ip_from, ip_to);"
    #cursor.execute(query)
    #connection.commit()

    with open(IP2COUNTRY_DB, 'r',  encoding='utf-8', errors='ignore') as db: 
        
        database = []
        for row in db:
            row = row.split('|')
            entry =   (bin(int(row[0]))[2:].zfill(128), bin(int(row[1]))[2:].zfill(128), row[2], row[3], row[4],row[5], row[6], row[7].strip('\n'))
            database.append(entry)
           
        query = """
                INSERT INTO ip2country 
                        VALUES (?,?,?,?,?,?,?,?)  
                """    
       
        cursor.executemany(query, database)
        connection.commit()
        connection.close()

        # To query transform ip into integer and integer to a fixed 128 bit value 

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
#print(read_mmdb("131.255.44.4"))
#print(read_mmdb("2c0f:eca0::0001"))

def extract_as_mysql(file=IP2COUNTRY_DB):

    with open(IP2COUNTRY_DB_MYSQL, 'w',  encoding='utf-8', errors='ignore') as f, open(IP2COUNTRY_DB, 'r',  encoding='utf-8', errors='ignore') as db: 
       
        f.write("CREATE TABLE ip2country\n(ip_from VARCHAR(50), ip_to VARCHAR(50),cc VARCHAR(3),registry VARCHAR(15), last_modified VARCHAR(15), record_type VARCHAR(2), status VARCHAR(30), description VARCHAR(255), PRIMARY KEY(ip_from, ip_to));\n")
        f.write("INSERT INTO ip2country (ip_from, ip_to, country, registry, last_modified, record_type, status, description)\n")
        f.write("VALUES\n")
        
        database = []
        for row in db:
            row = row.split('|')
            database.append(row)

        for row in database[:-1]:
            line = "('%s', '%s', '%s', '%s', '%s' , '%s', '%s', '%s'),\n" % (str(ipaddress.ip_address(int(row[0]))), str(ipaddress.ip_address(int(row[1]))), row[2], row[3], row[4],row[5], row[6], row[7].strip('\n'))
            f.write(line)
        else:
            line = "('%s', '%s', '%s', '%s', '%s' , '%s', '%s', '%s');" % (str(ipaddress.ip_address(int(row[0]))), str(ipaddress.ip_address(int(row[1]))), row[2], row[3], row[4],row[5], row[6], row[7].strip('\n'))
            f.write(line)

    # query with: Select country from ip2country where inet6_aton('41.31.255.254') >= inet6_aton(ip_to) and inet6_aton('41.31.255.254') <= inet6_aton(ip_to)

def testquery_sql_lite(nr_samples):
    with open(IP2COUNTRY_DB, 'r',  encoding='utf-8', errors='ignore') as db: 
       
        database = []
        for row in db:
            row = row.split('|')
            database.append(row)

    sample_values = []
    
    for i in range(1,nr_samples):
        sample_values.append(random.randint(0, len(database))) 

            
    query_values = []
    for index in sample_values:
        entry = database[index]
        ip_from = int(entry[0])
        ip_to = int(entry[1])
        query_values.append([bin(ip_from)[2:].zfill(128), bin(ip_to)[2:].zfill(128)])

    #print(result)
    
    start_time = time.time()  
    for value in query_values: 
        connection = sqlite3.connect(IP2COUNTRY_DB_SQLLITE)
        cursor = connection.cursor()
        query = "SELECT country FROM ip2country WHERE ip_from <= '%s' and ip_to >= '%s'" % (value[0], value[0])
        cursor.execute(query)
        result = cursor.fetchall()
        
    end_time = time.time()
    print("total time needed was:", f'{end_time - start_time:.3f}', "s\n") 
    print("Average time for one request: ", str((end_time - start_time) / nr_samples), "s")
    connection.close()     

def testquery_df(nr_samples):
    with open(IP2COUNTRY_DB, 'r',  encoding='utf-8', errors='ignore') as db: 
       
        database = []
        for row in db:
            row = row.split('|')
            database.append(row)

    sample_values = []
    
    for i in range(1,nr_samples):
        sample_values.append(random.randint(0, len(database))) 
            
    query_values = []
    for index in sample_values:
        entry = database[index]
        ip_from = int(entry[0])
        ip_to = int(entry[1])
        query_values.append([ip_from, ip_to])

    start_time = time.time() 
    
    for value in query_values: 
        df = pd.read_pickle(IP2COUNTRY_DB_DF)
        record = df.loc[ ( (df['ip_from'] <= ip) & (df['ip_to'] >= ip) ) ].values 
   
    end_time = time.time()
    print("total time needed was:", f'{end_time - start_time:.3f}', "s\n") 
    print("Average time for one request: ", str((end_time - start_time) / nr_samples), "s")
    
#extract_as_sqllite()
#testquery_sql_lite(100)

def comparedbs(nr_samples):

    with open("ipc.db", 'r') as cdb:

        c_db = []
        for entry in cdb:
            c_db.append(entry.split(" "))

    with open(IP2COUNTRY_DB, 'r',  encoding='utf-8', errors='ignore') as db: 
       
        database = []
        for row in db:
            row = row.split('|')
            database.append(row)

    sample_values = []
    
    for i in range(1,nr_samples):
        sample_values.append(random.randint(0, len(c_db))) 
            
    query_values = []
    for index in sample_values:
        entry = c_db[index]
        ip_from = int(entry[0])
        ip_to = int(entry[1])
        country = entry[2]
        query_values.append([ip_from, ip_to, country])

    col_names = ["ip_from", "ip_to", "country", "registry", "last-modified", "record_type", "status",  "description"]
    df = pd.read_csv(IP2COUNTRY_DB, delimiter="|", names=col_names, converters={'ip_from':int, 'ip_to':int })

    start_time = time.time() 

    i = 1
    eu_count = 0
    no_match = 0
    for entry in query_values:
        ip = int(entry[0]) +1
        country = entry[2].strip('\n')

        record = df.loc[ ( (df['ip_from'] <= ip) & (df['ip_to'] >= ip) ) ].values
        result = record[0][2]
        #print("%s: Country from C database %s, country from result %s" % (i,country, result))
        if result != country:
            no_match += 1
            print("%s: Country from C database %s with ip: %s, country from result %s" % (i,country, str(ipaddress.ip_address(ip)), result))
            if country == 'EU':
                eu_count += 1

        i += 1

    print("\nTotal entries looked at: %s" % i)
    print("No match cases: %s" % no_match)
    matching = (1 - (no_match / i)) * 100
    print("Old database matches new database to %s%%\n" % matching)
    print("EU cases: %s" % eu_count)

    end_time = time.time()
    print("total time needed was:", f'{end_time - start_time:.3f}', "s\n") 

