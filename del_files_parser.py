from multiprocessing.sharedctypes import Value
import re
import os
import shutil
import fileinput
import ipaddress
import time

from config import *;


# Release 0.9.0 coming soon ... 

# @TODO check if number of entries in ip2country_2.db is reasonable                         # Aufwand 5/8
# Number of entries is much less than the inetnum files ... 

# @TODO Speed up parsing process of inetnum files                                           # Aufwand 13/20
    # 01. External Sorting Method (Merge Sort) 
    # 02. Parsing should be done by multiple threads

# @TODO Bugfix in parse_inet_group() -> see todo there ...                                  # Auufwand 5 

# @TODO add city information (when available) to the method parse_inet parse_inet_group     # Aufwand 3

# @TODO Bugfix in parse_inet_group                                                          # Aufwand 3
# first record of final database is 0.0.0.0 |255.255.255.255
# must be removed this file is coming from the apnic.db.inetnum

# @TODO overlapping beispiele genauer anschauen und versuchen zu reproduzieren ...          # Aufwand 5/8
# code was simply taken 1:1 from c++ code !!!!!!

# @TODO handle_ranges_overlapp append elements which will change the sorted                 # Aufwand 5
# database. Therefore replace the append command by insert, you neeed to get 
# the index at which the record must be added. 

# @TODO vergleichen der Ergebnisse mit den von dem alten Tool                               # Aufwand 5

# @TODO get_country_code() &  ip_in_range() auslagern:                                      # Aufwand 1
# Diese beide Methoden sollten wo anderes ausgelagert werden,                           
# da sie nur die Datenbank nachher auslesen und nach einem Eintrag 
# suchen und somit eigentlich nicht zum Parser gehören.

# @TODO later add parameters for the command line interpreter (cli)                         # Aufwand 5

# @TODO comment and write description for each method & clean code                          # Aufwand 5 

# @TODO Flussdiagramm vom Parser erstellen                                                  # Aufwand 5

# @TODO MAX MindDB API importieren zum testen und anschauen benutzen                        # Aufwand 8
# wie sie die Objekte einer Datenbank aufbauen ....


# ==============================================================================
# Delegation parsing methods 


def merge_del_files():

    try: 
        
        # merges the delegated files into a one file 
        with open(MERGED_DEL_FILE, "wb") as f:
            
            for del_file in [ 
                    os.path.join(DEL_FILES_DIR, AFRINIC['del_fname']), 
                    os.path.join(DEL_FILES_DIR, LACNIC['del_fname']),
                    os.path.join(DEL_FILES_DIR, ARIN['del_fname']),
                    os.path.join(DEL_FILES_DIR, APNIC['del_fname']), 
                    os.path.join(DEL_FILES_DIR, RIPE['del_fname'])
                    ]:

                with open(del_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


def parse_del_files():

    try:

        with open(STRIPPED_DEL_FILE, "w") as f:

            for line in fileinput.input(MERGED_DEL_FILE):
                
                # get rid of all lines without "ip entry" before parsing
                if re.search(IPV4_PATTERN, line) or re.search(IPV6_PATTERN, line):

                    line = parse_del_line(line)
                    line = "|".join(map(str, line))
                    line = line + '\n'
                    f.write(line)

    except IOError as e:
        
        print(e)


def parse_del_line(line):          
    
    # record index:     0      1   2    3     4     5    6
    # record format: registry|cc|type|start|value|date|status[|extensions...]

    record = []
    record = line.split("|")

    # extract infromation from line
    registry    = record[0]
    country     = record[1]
    type        = record[2]
    network_ip  = record[3]
    mask        = record[4]
    status      = record[6]

    # convert name of ripencc (parser compatibilty) 
    if registry.lower() == 'ripencc':
        registry = "RIPE"

    # calculate int value of network ip
    range_start = int(ipaddress.ip_address(network_ip))
    range_end   = 0

    # if line doesn't have any country
    if status == "reserved" or status == "available":
        country = "ZZ"
    
    # parse ipv4 
    if type == "ipv4":
        range_end = range_start + int(mask) - 1

    # parse ipv6 
    if  type == "ipv6":
        net = ipaddress.IPv6Network(network_ip + "/" + mask)
        range_end = int(net.broadcast_address)

    return [range_start, range_end, country, registry]


# ==============================================================================
# Inetnum Parsing methods 

def merge_inet_files():
    
    try: 
        
        with open(MERGED_INET_FILE, "wb") as f:
            
            for inet_file in [ 
                    os.path.join(DEL_FILES_DIR, APNIC['inet_fname']), 
                    os.path.join(DEL_FILES_DIR, RIPE['inet_fname'])
                    ]:

                with open(inet_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


# Parses merged_ine file and writes it into stripped_ine_file
def parse_inet_files():
    
    with open(MERGED_INET_FILE, 'r', encoding='utf-8', errors='ignore') as merged, open (STRIPPED_INET_FILE, 'w', encoding='utf-8', errors='ignore') as stripped:
        
        for group in get_groups(merged, "inetnum"):
            
            line = parse_inet_group(group)
            line = "|".join(map(str, line))
            line = line + '\n'
            stripped.write(line)


# Returns block of data
def get_groups(seq, group_by):
    
    data = []
    
   
    for line in seq:
        
        # escape comments (starts with '#')
        # escape unrelevant data in ripe.inetnum (starts with '%')
        if line.startswith("#") or line.startswith("%"): 
            continue

        # every inetnum object starts with an entry -> inetnum: ...
        # so start grouping if a line starts with 'inetnum'
        # if an object has already been initialized then scann also the
        # next lines (or data) 
        if (line.startswith(group_by) or data) and not line.startswith("\n"):
        
            line = line.replace(" ", "").replace("\n", "")
            data.append(line)
            
        # note that empty lines are used as a seperator between
        # inetnum objects. So if line starts with empty line
        # then yield the data object first and then
        # reset the object to store next object's data
        elif line.startswith("\n") and data:
            yield data
            data = []


# Parses in entry
def parse_inet_group(entry):
    
    record = {}
    
    # remove all empty elements in the entry
    entry = [item for item in entry if item] 

    # split each element (e.g. ["source:APNIC" in the entry to  ["source", "APNIC"]
    entry = [item.split(':', maxsplit = 1) for item in entry]
    
    # create a dictionary
    # if there are dupplicate items append their values ..
    # this will prevent deleting items with same key (e.g. descr)
    for item in entry:
      
            # @TODO without this IndexError is thrown
            if(len(item) > 1):

                key = item[0]
                value = item[1]
                
                if key not in record:
                    record[key] = value
                
                if key == "descr":
                    record[key] = record[key] + " " + value

                # if a country line has comment, remove the comment
                if key == "country":
                    record[key] = value.split("#")[0]

                if key == "source" and value == "ripencc":
                    record[key] = "RIPE"

    # extract the ranges out of record
    range       = record['inetnum'].split("-")
    range_start = int(ipaddress.ip_address(range[0]))
    range_end   = int(ipaddress.ip_address(range[1]))
    
    country     = record['country']
    registry    = record['source']
    
    if 'descr' in record:
        descr = record['descr']
        return [range_start, range_end, country, registry, descr]

    return [range_start, range_end, country, registry]


# ==============================================================================
# Help Methods used for all files ... 


def sort_file(file):

    records = []

    try:

        # save all records into a list
        with open(file, "r", encoding='utf-8', errors='ignore') as f:
            
            for line in f:
                
                if line.startswith("\n"):
                    continue

                line = line.split("|")
            
                record = [
                    int(line[0]),                   # get range_start
                    int(line[1]),                   # get range_end
                    line[2],                        # country
                    line[3].rstrip('\n').upper()    # register 
                ]

                records.append(record)

                
        # sort this list
        records.sort()

        # write it back 
        with open(file, "w", encoding='utf-8', errors='ignore') as f:
            
            for record in records:
               
               line = "|".join(map(str, record))
               line = line + "\n"
               f.write(line)
               

    except IOError as e:
        
        print(e)

    return records


def check_for_overlaping(file):
    
    records = []

    try:

        # save all records in stripped_del_file into a list
        with open(file, "r", encoding='utf-8', errors='ignore') as f:
            
            for line in f:
                
                if line.startswith("\n"):
                    continue

                line = line.split("|")
                
                record = [
                    int(line[0]),                   # range_start
                    int(line[1]),                   # range_end
                    line[2],                        # country
                    line[3].rstrip('\n').upper()    # register
                ]
                
                records.append(record)
            
        # check if two records overlapps
        # since that the list is sorted, overlapping
        # may only occur in successive records (record[i] and record[i+1])
        nr_of_overlapps = 0
        for i in range(1, len(records)-1):
            
            if records[i] and records[i-1]:
                
                overlapp = ip_ranges_overlapp(records[i-1], records[i])
                
                if overlapp :
                    nr_of_overlapps = nr_of_overlapps + 1
                    handle_ranges_overlapp(records[i-1], records[i], records)

        print(f"{nr_of_overlapps} overlapps were found and resolved")

        # remove all empty items (unvalid) ...
        records = filter(lambda record: len(record) > 0, records)
        records = list(records)


        with open(file, "w", encoding='utf-8', errors='ignore') as f:
            
            for record in records:
                
                line = "|".join(map(str, record))
                line = line + '\n'
                f.write(line)

    
    except IOError as e:
        
        print(e)


def handle_ranges_overlapp(record_1, record_2, records):
    
    # if the cause of the conflict is RIPE then change RIPE 
    # entry to remove the confilct
    if record_1[3]  == "RIPE" or record_2[3] == "RIPE":

        if record_1[3] == "RIPE":

            if (record_1[0] == record_2[0] and record_1[1] == record_2[1]) or record_1[1] < record_2[1]:
                record_1 = record_1.clear()

            elif (record_1[0] < record_2[0] and record_1[1] == record_2[1]) or (record_1[1] >= record_2[0] and record_1[1] <= record_2[1]):
                record_1[1] = record_2[0] - 1

            elif record_1[0] < record_2[0] and record_1[1] > record_2[1]:
                record = [
                    record_2[1] + 1,
                    record_1[1],
                    record_1[2],
                    record_1[3]
                ]
                
                records.append(record)
                record_1[1] = record_2[0] - 1

        else :

            if record_1[0] <= record_2[0] and record_1[1] >= record_2[1]:
                record_2 = record_2.clear()
            
            elif record_1[0] <= record_2[0] and record_1[1] >= record_2[0] and record_1[1] < record_2[1]:
                record_2[0] = record_1[1] + 1

    # if the conflict is between entries except ripe then the change is made on the
    # first entry that cause the conflict        
    else: 

        if (record_1[0] == record_2[0] and record_1[1] == record_2[1]) or record_1[1] < record_2[1]:
            record_1 = record_1.clear()

        elif (record_1[0] < record_2[0] and record_1[1] == record_2[1]) or (record_1[1] >= record_2[0] and record_1[1] <= record_2[1]):
            record_1[1] = record_2[0] - 1

        elif record_1[0] < record_2[0] and record_1[1] > record_2[1]:
            record = [
                record_2[1] + 1,
                record_1[1],
                record_1[2],
                record_1[3]
            ]
            
            records.append(record)
            record_1[1] = record_2[0] - 1


def ip_ranges_overlapp(record_1, record_2):

    range_end_1     = record_1[1]
    range_start_2   = record_2[0]

    # case 1: [1, 3] [2, 4] -> 2 < 3 overlapping
    # case 2: [1, 3] [3, 4] -> 3 = 3 overlapping
    return  range_end_1 >= range_start_2 


def merge_databases():
    
    try: 
        
        # merges the delegated files into a one file 
        with open(IP2COUNTRY_DB, "wb") as f:
            
            for del_file in [ 
                    os.path.join(STRIPPED_DEL_FILE), 
                    os.path.join(STRIPPED_INET_FILE),
                    ]:

                with open(del_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
 
    except IOError as e:
        
        print(e)


# ==============================================================================
# @TODO 
# Diese beide Methoden sollten wo anderes ausgelagert werden (e.g. lib.py),
# da sie nur die Datenbank nachher auslesen und nach einem Eintrag 
# suchen und somit eigentlich nicht zum Parser gehören.

def get_country_code(ip):

    with open(STRIPPED_DEL_FILE) as file:

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


# ==============================================================================
# Parser Entry Method 
# @TODO later add parameters for the command line interpreter (cli)

def deltempFiles():
    os.remove(MERGED_DEL_FILE)
    os.remove(STRIPPED_DEL_FILE)
    os.remove(MERGED_INET_FILE)
    os.remove(STRIPPED_INET_FILE)


def run_parser():

    start_time = time.time()
    print("parsing Started\n")

    print("merging delegation files ...")
    merge_del_files()          
    print("merging finished\n")

    print("parsing delegation files ...")
    parse_del_files()           
    print("parsing finished\n")

    print("merging inetnum files ...")
    merge_inet_files()
    print("merging finished\n")

    print("parsing inetnum files ...")
    parse_inet_files()
    print("parsing finished\n")

    print("creating the final database ...")
    merge_databases()
    
    print("sorting the final data base\n")
    sort_file(IP2COUNTRY_DB)
    check_for_overlaping(IP2COUNTRY_DB)
    print("finished\n")

    end_time = time.time()
    print("Total time needed was:", f'{end_time - start_time:.3f}', "s\n")  # (Mohammad: 182,006s) (Thomas: 1112,578s)

    #deltempFiles()
    return 0

run_parser()


# For testing, prints overlapps in the database:

# with open(os.path.join(DEL_FILES_DIR, "ip2country_2.db"), "r") as f:

#     records = [] 

#     for line in f:
        
#         if line.startswith("\n"):
#             continue

#         line = line.split("|")
        
#         record = [
#             int(line[0]),           # range_start
#             int(line[1]),           # range_end
#             line[2],                # country
#             line[3].rstrip('\n')    # register
#         ]

#         records.append(record)

# # check if two records overlapps
# # since that the list is sorted, overlapping
# # may only occur in successive records (record[i] and record[i+1])
# for i in range(1, len(records)-1):

#     overlapp = ip_ranges_overlapp(records[i-1], records[i])
    
#     if overlapp :
#         print(records[i-1])
#         print(records[i])
#         print("\n")