from queue import Empty
import re
import os
import shutil
import fileinput
import ipaddress

from config import *;


# Simple version ohne Optimierung und Städte unterstützung

# @TODO beispiele genauer anschauen und versuchen zu reproduzieren ...

# @TODO MAX MindDB API anschauen benutzen 
# wie sie die Objekte einer Datenbank aufbauen ....

# @TODO vergleichen der Ergebnisse mit den von dem 
# alten Tool 

# @TODO check if -1 is giving the right broadcast in parse_line

def merge_del_files():

    try: 
        
        # merges the delegated files into a one file 
        with open(MERGED_DEL_FILE, "wb") as f:
            
            for del_file in [ 
                    os.path.join(DEL_FILES_DIR, AFRINIC['fname']), 
                    os.path.join(DEL_FILES_DIR, LACNIC['fname']),
                    os.path.join(DEL_FILES_DIR, ARIN['fname']),
                    os.path.join(DEL_FILES_DIR, APNIC['fname']), 
                    os.path.join(DEL_FILES_DIR, RIPE['fname'])
                    ]:

                with open(del_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


def strip_del_files():

    try:

        with open(STRIPPED_DEL_FILE, "w") as f:

            for line in fileinput.input(MERGED_DEL_FILE):
                
                # get rid of all lines without "ip entry" before parsing
                if re.search(IPV4_PATTERN, line) or re.search(IPV6_PATTERN, line):

                    line = parse_line(line)
                    line = "|".join(map(str, line))
                    line = line + '\n'
                    f.write(line)

    except IOError as e:
        
        print(e)


def parse_line(line):          
    
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
        country = "N/A"
    
    # parse ipv4 
    if type == "ipv4":
        range_end = range_start + int(mask) - 1

    # parse ipv6 
    if  type == "ipv6":
        net = ipaddress.IPv6Network(network_ip + "/" + mask)
        range_end = int(net.broadcast_address)

    return [range_start, range_end, country, registry]


def sort_del_files():

    records = []

    try:

        # save all records in stripped_del_file into a list
        with open(STRIPPED_DEL_FILE, "r") as f:
            
            for line in f:
               
                line = line.split("|")

                record = [
                    int(line[0]),           # get range_start
                    int(line[1]),           # get range_end
                    line[2],                # country
                    line[3].rstrip('\n')    # register
                ]

                records.append(record)

        
        # sort this list
        records.sort()

        # write it back 
        with open(STRIPPED_DEL_FILE, "w") as f:
            
            for record in records:
               
               line = "|".join(map(str, record))
               line = line + '\n'
               f.write(line)
               

    except IOError as e:
        
        print(e)

    return records


def check_for_overlaping():
    
    records = []

    try:

        # save all records in stripped_del_file into a list
        with open(STRIPPED_DEL_FILE, "r") as f:
            
            for line in f:
               
                line = line.split("|")
                
                record = [
                    int(line[0]),           # range_start
                    int(line[1]),           # range_end
                    line[2],                # country
                    line[3].rstrip('\n')    # register
                ]

                records.append(record)
        
        for i in range(1, len(records)-1):
        
            overlapp = ip_ranges_overlapp(records[i-1], records[i])
            
            if overlapp :
                
               handle_ranges_overlapp(records[i-1], records[i], records)
        
        # remove all empty items (unvalid) ...
        records = filter(lambda record: len(record) > 0, records)
        records = list(records)


        with open(STRIPPED_DEL_FILE, "w") as f:
            
            for record in records:
                
                line = "|".join(map(str, record))
                line = line + '\n'
                f.write(line)

    
    except IOError as e:
        
        print(e)


def handle_ranges_overlapp(record_1, record_2, records):
    
    # if the cause of the conflict is ripencc then change ripencc 
    # entry to remove the confilct
    if record_1[3] == "ripencc" or record_2[3] == "ripencc":

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
     
    range_start_1   = record_1[0]
    range_end_1     = record_1[1]
    range_start_2   = record_2[0]
    range_end_2     = record_2[1]
    
    if(range_end_1 < range_start_2 ):   # [1, 2] [3, 4] -> 2 < 3 no overlapping 
        return False
    
    return  range_end_1 > range_start_2 # [1, 3] [2, 4] -> 2 < 3 overlapping 


def get_country_code(ip):

    with open(STRIPPED_DEL_FILE) as file:

        for line in file:

            item = line.split("|")

            range_start = int(item[0])
            range_end   = int(item[1])
            country     = item[2].rstrip('\n')

            if ip_in_range(ip, range_start, range_end):

                if country == 'N/A':
                    return country
                
                return COUNTRY_DICTIONARY[country], country
    
    return False


def ip_in_range(ip, start, end):
    
    ip = ipaddress.ip_address(ip)
    ip_int = int(ip)

    return start <= ip_int <= end 


# merge_in_files
def merge_in_files():
    
    try: 
        
        with open(os.path.join(DEL_FILES_DIR, "merged_ine_file.txt"), "wb") as f:
            for in_file in [ 
                    os.path.join(DEL_FILES_DIR, "apnic.db.inetnum"), 
                    #os.path.join(DEL_FILES_DIR, "ripe.db.inetnum")
                    ]:

                with open(in_file, "rb") as source:

                    shutil.copyfileobj(source, f)

                    f.write(os.linesep.encode())
    
    except IOError as e:
        
        print(e)


# Returns block of data
def get_groups(seq, group_by):
    data = []
    for line in seq:
        if line.startswith(group_by):
            if data:
                if not data[0].startswith(group_by):
                    data = []
                else:
                    yield data[:-1]
                    data = []
        data.append(line.replace(" ", "").replace('\n', ""))

    if data:
        yield data


# Parses in entry
def get_parsed_in_entry(entry):
    y = []
    description = ""
    for item in entry:
        try:
            
            if any(str(item[0]) in s for s in PARSE_ITEMS):

                if not item[0] == "descr":
                    y.append(item[1])
                else:
                    description += item[1] + ' '
        
        # @TODO
        except IndexError as e:
            pass
    
    y.append(description[:-1])

    return y

# Parses merged_ine file and writes it into stripped_ine_file
def parse_in_files():
    with open(os.path.join(os.path.join(DEL_FILES_DIR, "merged_ine_file.txt")), 'r', encoding='utf-8', errors='ignore') as merged, open (os.path.join(DEL_FILES_DIR, "stripped_ine_file.txt"), 'w', encoding='utf-8', errors='ignore') as stripped:
        for i, group in enumerate(get_groups(merged, "inetnum"), start=1):
            
            entry = [item.split(':') for item in group]
            #entry = [re.split(r': +', item) for item in group] # funktioniert nicht warum?
            stripped.write("|".join(get_parsed_in_entry(entry)) + '\n')

    #os.remove(os.path.join(DEL_FILES_DIR, "merged_ine_file.txt"))

def run_parser():

    print("Merging delegation files ...")
    merge_del_files()          # Fügt del Dateien in del_merged zusammen
    print("Delegation files merging finished\n")

    print("Striping merged file ...")
    strip_del_files()           # formatiert del_merged 
    print("Striping merged file finished\n")

    print("Sorting striped file ...")
    sort_del_files()            # sortiert del_stripped
    print("Sorting striped files finished\n")

    print("checking for overlapping ...")
    check_for_overlaping()     # clean del_stripped from overlapping in data
    print("checking for overlapping finished\n")
    
    return 0

run_parser()

#merge_in_files()
#parse_in_files()        

# l = ['202.6.91.0-202.6.91.255', 'NLA', 'AU', 'ASSIGNEDPORTABLE', '2008-09-04T06', 'APNIC', ['NationalLibraryofAustralia ParkesPlace CanberraACT2600']]


# Overlapping example
# ripencc|DE|ipv4|202.71.144.0|2048|19990830|allocated
# apnic|IN|ipv4|202.71.144.0|2048|19990830|allocated
