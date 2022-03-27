from multiprocessing.sharedctypes import Value
from queue import Empty
import re
import os
import shutil
import fileinput
import ipaddress
import time
from warnings import catch_warnings

from config import *;


# Simple version ohne Optimierung und Städte unterstützung

# @TODO Flussdiagramm vom Parser erstellen 

# @TODO overlapping beispiele genauer anschauen und versuchen zu reproduzieren ...

# @TODO vergleichen der Ergebnisse mit den von dem 
# alten Tool 

# @TODO MAX MindDB API anschauen benutzen 
# wie sie die Objekte einer Datenbank aufbauen ....


# ==============================================================================
# Delegation files methods 


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
                if re.search(IPV4_PATTERN, line) :#or re.search(IPV6_PATTERN, line):

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

    #os.remove(os.path.join(DEL_FILES_DIR, "merged_ine_file.txt"))

# Returns block of data
def get_groups(seq, group_by):
    
    data = []
    
   
    for line in seq:
        
        # escape comments (starts with '#') and empty lines
        # escape unrelevant data in ripe.inetnum begins with '%'
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

    # extract the ranges out of record
    range       = record['inetnum'].split("-")
    range_start = int(ipaddress.ip_address(range[0]))
    range_end   = int(ipaddress.ip_address(range[1]))
    
    country     = record['country']
    registry    = record['source']

    return [range_start, range_end, country, registry]


# ==============================================================================
# Help Methods used for all files ... 


def sort_file(file):

    records = []

    try:

        # save all records into a list
        with open(file, "r") as f:
             
            for line in f:
                
                if line.startswith("\n"):
                    continue

                line = line.split("|")
            
                record = [
                    int(line[0]),           # get range_start
                    int(line[1]),           # get range_end
                    line[2],                # country
                    line[3]                 # register 
                ]

                records.append(record)

                
        # sort this list
        records.sort()

        # write it back 
        with open(file, "w") as f:
            
            for record in records:
               
               line = "|".join(map(str, record))
               line = line + '\n'
               f.write(line)
               

    except IOError as e:
        
        print(e)

    return records


def check_for_overlaping(file):
    
    records = []

    try:

        # save all records in stripped_del_file into a list
        with open(file, "r") as f:
            
            for line in f:
               
                line = line.split("|")
                
                record = [
                    int(line[0]),           # range_start
                    int(line[1]),           # range_end
                    line[2],                # country
                    line[3].rstrip('\n')    # register
                ]
                
                records.append(record)
            
        # check if two records overlapps
        # since that the list is sorted, overlapping
        # may only occur in successive records (record[i] and record[i+1])
        for i in range(1, len(records)-1):
            
            # @TODO IndexError !!!
            if records[i] and records[i-1]:

                overlapp = ip_ranges_overlapp(records[i-1], records[i])
                
                if overlapp :
                    
                    handle_ranges_overlapp(records[i-1], records[i], records)

        # remove all empty items (unvalid) ...
        records = filter(lambda record: len(record) > 0, records)
        records = list(records)


        with open(file, "w") as f:
            
            for record in records:
                
                line = "|".join(map(str, record))
                line = line + '\n'
                f.write(line)

    
    except IOError as e:
        
        print(e)


def handle_ranges_overlapp(record_1, record_2, records):
    
    # if the cause of the conflict is ripencc then change ripencc 
    # entry to remove the confilct
    if record_1[3]  == "ripencc" or record_2[3] == "ripencc":

        if record_1[3] == "ripencc":

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
        with open(os.path.join(DEL_FILES_DIR, "ip2country_2.db"), "wb") as f:
            
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
# Diese beide Methoden sollten wo anderes ausgelagert werden,
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

def run_parser():

    start_time = time.time()
    print("parsing Started\n")

    # print("merging delegation files ...")
    # merge_del_files()          # Fügt del Dateien in del_merged zusammen
    # print("merging finished\n")

    # print("parsing delegation files ...")
    # parse_del_files()           # formatiert del_merged 
    # print("parsing finished\n")

    # print("merging inetnum files ...")
    # merge_inet_files()
    # print("merging finished\n")

    # print("parsing inetnum files ...")
    # parse_inet_files()
    # print("parsing finished\n")

    # print("creating the final database ...")
    # merge_databases()
    
    # print("sorting the final data base")
    # sort_file(os.path.join(DEL_FILES_DIR, "ip2country_2.db"))
    
    check_for_overlaping(os.path.join(DEL_FILES_DIR, "ip2country_2.db"))
    
    end_time = time.time()
    print("parsing finished", end = " -> ")
    print("Total time needed was:", f'{end_time - start_time:.3f}', "s")

    return 0

#run_parser()


# l = ['202.6.91.0-202.6.91.255', 'NLA', 'AU', 'ASSIGNEDPORTABLE', '2008-09-04T06', 'APNIC', ['NationalLibraryofAustralia ParkesPlace CanberraACT2600']]


# Overlapping example
# ripencc|DE|ipv4|202.71.144.0|2048|19990830|allocated
# apnic|IN|ipv4|202.71.144.0|2048|19990830|allocated


# save all records in stripped_del_file into a list
# with open(STRIPPED_INET_FILE, "r") as f:

#     records = [] 

#     for line in f:
        
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
#         break
